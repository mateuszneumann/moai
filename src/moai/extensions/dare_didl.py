
from lxml import etree
from lxml.builder import ElementMaker
from lxml.etree import SubElement

from moai import MataDataPrefix, name
from moai.metadata import OAIDC, MODS, XSI_NS

        
class DIDL(MataDataPrefix):
    
    name('didl')
    
    def __init__(self, prefix, config, db):
        self.prefix = prefix
        self.config = config
        self.db = db

        self.ns = {'didl': "urn:mpeg:mpeg21:2002:02-DIDL-NS",
                   'dii': "urn:mpeg:mpeg21:2002:01-DII-NS",
                   'dip': "urn:mpeg:mpeg21:2002:01-DIP-NS",
                   'dcterms': "http://purl.org/dc/terms/",
                   'xsi': "http://www.w3.org/2001/XMLSchema-instance",
                   'dc': 'http://purl.org/dc/elements/1.1/',
                   }

        self.schemas = {'didl':'http://standards.iso.org/ittf/PubliclyAvailableStandards/MPEG-21_schema_files/did/didl.xsd',
                        'dii': 'http://standards.iso.org/ittf/PubliclyAvailableStandards/MPEG-21_schema_files/dii/dii.xsd',
                        'dip': 'http://standards.iso.org/ittf/PubliclyAvailableStandards/MPEG-21_schema_files/dip/dip.xsd'}
        
    def __call__(self, element, metadata):
        data = metadata.record
        
        DIDL = ElementMaker(namespace=self.ns['didl'], nsmap=self.ns)
        DII = ElementMaker(namespace=self.ns['dii'])
        DIP = ElementMaker(namespace=self.ns['dip'])
        DCTERMS = ElementMaker(namespace=self.ns['dcterms'])

        oai_url = self.config.url+'?verb=GetRecord&metadataPrefix=dare_didl&identifier=%s' % (
            self.config.get_oai_id(data['record']['id']))

        # generate oai_dc for this feed
        oai_dc_data = DIDL.Resource(mimetype="application/xml")
        OAIDC('oai_dc', self.config, self.db)(oai_dc_data, metadata)
        # generate mods for this feed
        mods_data = DIDL.Resource(mimetype="application/xml")
        MODS('mods', self.config, self.db)(mods_data, metadata)

        asset_data = []
        
        didl = DIDL.DIDL(
            DIDL.Item(
             DIDL.Descriptor(
              DIDL.Statement(
               DII.Identifier(data['metadata'].get('dare_id', [''])[0]),
              mimeType="application/xml")
              ),
             DIDL.Descriptor(
              DIDL.Statement(
               DCTERMS.modified(data['record']['when_modified'].isoformat().split('.')[0]),
               mimeType="application/xml"
               )
              ),
             DIDL.Component(
              DIDL.Resource(ref=oai_url,mimeType="application/xml")
              ),
             DIDL.Item(
              DIDL.Descriptor(
               DIDL.Statement(
                DIP.ObjectType('info:eu-repo/semantics/descriptiveMetadata'),
                mimeType="application/xml")
               ),
              DIDL.Component(oai_dc_data)
              ),
             DIDL.Item(
              DIDL.Descriptor(
               DIDL.Statement(
                DIP.ObjectType('info:eu-repo/semantics/descriptiveMetadata'),
                mimeType="application/xml")
               ),
              DIDL.Component(mods_data)
              ),
             DIDL.Item(
              DIDL.Descriptor(
               DIDL.Statement(
                DIP.ObjectType('info:eu-repo/semantics/humasStartPage'),
                mimeType="application/xml")
                ),
              DIDL.Component(
               DIDL.Resource(mimetype="text/html", ref=data['metadata'].get('url', [''])[0])
               )
              ),
             )
            )

        for root_item in didl:
            for asset in data['metadata'].get('asset', []):
                item = DIDL.Item(
                    DIDL.Descriptor(
                     DIDL.Statement(
                      DIP.ObjectType('info:eu-repo/semantics/humasStartPage'),
                      mimeType="application/xml")
                     ),
                    DIDL.Component(
                     DIDL.Resource(mimetype=asset['mimetype'],
                                   ref=asset['url'])
                     )
                    )
                root_item.append(item)
            break
        
        
        didl.attrib['{%s}schemaLocation' % XSI_NS] = '%s %s %s %s %s %s' % (self.ns['didl'],
                                                                            self.schemes['didl'],
                                                                            self.ns['dii'],
                                                                            self.schemes['dii'],
                                                                            self.ns['dip'],
                                                                            self.schemes['dip'])
        element.append(didl)