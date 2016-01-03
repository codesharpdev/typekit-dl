#!/usr/bin/env python
#encoding: utf-8

from urllib2 import *
import json
try:
    import fontforge
except ImportError:
    raise Exception, "Este script requiere el módulo fontforge para funcionar."


HELP_MESSAGE = '''
Script en Python para descargar tipografías de Typekit.com

Para funcionar correctamente necesita Fontforge y su módulo para Python
(http://fontforge.org/python.html). En Ubuntu/Debian el módulo puede instalarse con:

~$ apt-get install python-fontforge

El script descarga el css que contiene la tipografía codificada en base64.
A continuación la extrae y usando Fontforge crea fuentes en formato ttf, eot, otf,
woff y svg. También construye un "facefont kit" para usar la tipografía
como webfont sin necesidad de depender de Typekit.

Modo de uso:

~$ ./typekit-dl.py [URL de la tipografía] [Ruta a carpeta de destino]

Ejemplo:

~$ ./typekit-dl.py https://typekit.com/fonts/myriad-pro /home/jorge/Myriad
'''

pattTokenFileUrl = 'browse-[abcdef\d]{32}\.js' # https://typekit.com/assets/browse-e4975a1e94a128f286a8d39206ae7d21.js
pattToken = '[abcdef\d]{234}'
pattFontInfoJson = 'familyDetailView.update\((.+)\)'
baseUrl = 'https://use.typekit.net/dp/tk/%s/%s/%s.otf?%s'


class DownloaderError(Exception):
    def __init__(self, msg=False):
        self.msg = msg

class TypekitDownloader():
    def __init__(self, typekitUrl):
        self.typekitUrl = typekitUrl

        pattUrl = 'https://(www\.)?typekit\.com/fonts/(.+)'

        match = re.match(pattUrl, typekitUrl)
        if not match:
            raise DownloaderError('\nLa dirección no es valida.')

        self.response = urlopen(typekitUrl)
        if self.response.code != 200:
            raise DownloaderError('\nError al conectar con Typekit: %d' % self.response.code)

        html = self.response.read()

        fontInfoJson = re.search(pattFontInfoJson, html).group(1)
        self.fontInfo = json.loads(fontInfoJson)
        self.fontName = self.fontInfo['name']
        self.fontSlug = self.fontInfo['slug']
        self.fontInfo = self.fontInfo['fonts']

        tokenFileUrl = re.search(pattTokenFileUrl, html).group()
        tokenFile = urlopen('https://typekit.com/assets/' + tokenFileUrl).read()
        self.token = re.search(pattToken, tokenFile).group()

    def fontDownloader(self, destinationFolder = False):

      if destinationFolder:
        self.fontfaceFolder = destinationFolder
      else:
        self.fontfaceFolder = self.fontName


      fontsFolder = self.fontfaceFolder + '/' + 'fonts'
      if not os.path.exists(fontsFolder):
        os.makedirs(fontsFolder)

      css = self.fontfaceFolder + '/' + self.fontName + '.css'  
      opener = build_opener()
      opener.addheaders = {('Referer', self.typekitUrl)}


      for item in self.fontInfo:

        alias = item['preview']['alias']
        fvd = item['preview']['fvd']
        subset = item['preview']['subset']

        fontUrl = baseUrl % (alias, fvd, subset, self.token)
        print fontUrl
        
        otf = opener.open(fontUrl).read()

        dump = fontsFolder + '/' + self.fontSlug +'-'+ item['name'].lower() + '.font'
        open(dump,'w+').write(otf)

        fontfactory = fontforge.open(dump, 1)
        fontfactory.fontname = self.fontName.replace(" ", "") + item["name"].replace(" ", "")
        fontfactory.familyname = self.fontName
        fontfactory.fullname = self.fontName + ' ' + item["name"]
        extensions = ['.eot', '.ttf', '.otf', '.svg', '.woff']
        for ext in extensions:

          fontfactory.generate(fontsFolder + '/' + fontfactory.fullname + ext)
        
        try:
          os.remove(dump)
          # for some reason, probably an error during conversion, an .afm file in created
          # the code bellow removes the .afm file if it does exists.
          os.remove(fontsFolder + '/' + fontfactory.fullname + '.afm')
        except:
          pass

        template = "@font-face {\
          \n\tfont-family: '" + fontfactory.fullname + "';\
          \n\tsrc: url('fonts/" + fontfactory.fullname + ".eot');\
          \n\tsrc: url('fonts/" + fontfactory.fullname + ".eot?#iefix') format('embedded-opentype'),\
          \n\turl('fonts/" + fontfactory.fullname + ".woff') format('woff'),\
          \n\turl('fonts/" + fontfactory.fullname + ".ttf') format('truetype'),\
          \n\turl('fonts/" + fontfactory.fullname + ".svg#ywftsvg') format('svg');\
          \n\tfont-style: normal;\
          \n\tfont-weight: normal;\
          \n}\n\n"

        open(css, 'a').writelines(template)

if __name__ == '__main__':
  args = sys.argv

  if len(args) == 1:
        
    print HELP_MESSAGE
    exit()

  try:
    downloader = TypekitDownloader(args[1])

    if len(args) == 3:
      destinationFolder = args[2]
    else:
      destinationFolder = False

      downloader.fontDownloader()
      print "\nOperación completada con éxito."
  except DownloaderError as error:
    print "\nError: %s\n" % error.msg
    print "Por favor, abra una issue en https://github.com/jorgegarciadev/typekit-dl/issues"
    exit(1)