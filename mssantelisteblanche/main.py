#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
import tempfile
import subprocess
from lxml import etree


URL_LISTEBLANCHE = "https://espacedeconfiance.mssante.fr/listeblanchemssante.xml"  # noqa
URL_CA = "http://igc-sante.esante.gouv.fr/AC/Chaine_de_certification-IGC-Sante.p7b"  # noqa


class CAError(Exception):
    pass


def p7b_to_pem(p7bdata):
    pipe = subprocess.Popen(
        [
            "openssl", "pkcs7", "-print_certs", "-outform", "PEM",
            "-text", "-in", "-"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE)
    stdout, stderr = pipe.communicate(p7bdata)
    if pipe.returncode == 0:
        return stdout
    else:
        raise CAError(stderr)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--listeblanche", default=URL_LISTEBLANCHE)
    parser.add_argument("--ca", default=URL_CA)
    args = parser.parse_args()

    with tempfile.NamedTemporaryFile(
            prefix="ca_igc_sante_", suffix=".pem") as caf:
        ca_resp = requests.get(args.ca)
        assert ca_resp.status_code == 200
        caf.write(p7b_to_pem(ca_resp.content))
        caf.flush()
        resp = requests.get(args.listeblanche, verify=caf.name)
        xmldata = resp.content
    root = etree.fromstring(xmldata)
    domains = root.xpath(
        u"//n:Domaine/n:Nom/text()",
        namespaces={'n': "https://listeblanche.mssante.fr/schema"})
    for d in [d.strip() for d in domains if d.strip()]:
        if sys.version_info >= (3, 0):
            print(d)
        else:
            print(d.encode("utf-8"))

if __name__ == "__main__":
    main()
