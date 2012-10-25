import urllib
import webbrowser
import urllib2
import zlib
import base64
def deflate(data, compresslevel=9):
    compress = zlib.compressobj(
            compresslevel,        # level: 0-9
            zlib.DEFLATED,        # method: must be DEFLATED
            -zlib.MAX_WBITS,      # window size in bits:
                                  #   -15..-8: negate, suppress header
                                  #   8..15: normal
                                  #   16..30: subtract 16, gzip header
            zlib.DEF_MEM_LEVEL,   # mem level: 1..8/9
            0                     # strategy:
                                  #   0 = Z_DEFAULT_STRATEGY
                                  #   1 = Z_FILTERED
                                  #   2 = Z_HUFFMAN_ONLY
                                  #   3 = Z_RLE
                                  #   4 = Z_FIXED
    )
    deflated = compress.compress(data)
    deflated += compress.flush()
    return deflated

def inflate(data):
    decompress = zlib.decompressobj(
            -zlib.MAX_WBITS  # see above
    )
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated

req="""
<?xml version="1.0"?>
<samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="aaf23196-1773-2113-474a-fe114412ab72" Version="2.0" IssueInstant="2012-07-16T17:34:59Z" AssertionConsumerServiceIndex="0" AttributeConsumingServiceIndex="0">
        <saml:Issuer>KeystoneClientSecure</saml:Issuer>
        <samlp:NameIDPolicy AllowCreate="true" Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient"/>
        <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
<SignedInfo>
<CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
<SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>
<Reference>
<Transforms>
<Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
</Transforms>
<DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
<DigestValue>k55e0liD2ForMykDFKAuyZ+ctew=</DigestValue>
</Reference>
</SignedInfo>
<SignatureValue>BUblScldZzF6esokmEsKrXXsy7gSbSormvgSxO121GHai/Q/ag4j3pV/pwyz7cOF
4Yes8bcxjO0FjvTKpN4UGmlc8IfxF2ipcMov57X0Igujh7NZh3robPv8q+ukP2Tr
KzfwotxCPbvK7//Q8usX/DHHxn3emkfn/6lCX3fzjoM=</SignatureValue>
<KeyInfo>
<KeyName>cert/privkey.pem</KeyName>
</KeyInfo>
</Signature></samlp:AuthnRequest>"""

req = deflate(req)

req = base64.b64encode(req)

req = urllib.urlencode({"SAMLRequest": req})

print req
