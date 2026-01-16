# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring
# pylint: disable=invalid-name,line-too-long

from tests.base import assets, main, copy_of_directory # pylint: disable=import-error, no-name-in-module
from ocrd import Resolver, Workspace
from ocrd_utils import MIMETYPE_PAGE, pushd_popd, initLogging, disableLogging
from ocrd_modelfactory import page_from_file
from ocrd.processor.base import run_processor
from ocrd.processor.builtin.shell_processor import ShellProcessor

from tests.test_mets_server import fixture_start_mets_server
from tests.processor.test_processor import workspace_kant


def test_cat_command(workspace_kant, caplog):
    caplog.set_level(10)
    workspace = workspace_kant
    input_files = workspace.mets.find_all_files(fileGrp='OCR-D-GT-PAGE')
    input_pcgts0 = page_from_file(input_files[0])
    proc = run_processor(ShellProcessor,
                         workspace=workspace,
                         input_file_grp="OCR-D-GT-PAGE",
                         output_file_grp="OCR-D-OUT",
                         parameter={'command': 'cat @INFILE > @OUTFILE'},
                         log_level='DEBUG')
    assert len(caplog.records) > 1
    assert any(rec.message.startswith("Executing processor 'ocrd-command' took")
               for rec in caplog.records
               if rec.name == 'ocrd.process.profile')
    assert sum(1 for rec in caplog.records
               if rec.name == 'ocrd.processor.ShellProcessor' and
               "returned: 0" in rec.message) == 2
    output_files = workspace.mets.find_all_files(fileGrp='OCR-D-OUT')
    assert len(input_files) == len(output_files)
    output_files.sort(key=lambda x: x.url)
    assert output_files[0].local_filename == 'OCR-D-OUT/OCR-D-OUT_PHYS_0017.xml'
    output_pcgts0 = page_from_file(output_files[0])
    assert output_pcgts0.pcGtsId == output_files[0].ID
    assert len(output_pcgts0.Page.get_AllTextLines()) == len(input_pcgts0.Page.get_AllTextLines())

def test_xml_roundtrip_command(workspace_kant, caplog):
    caplog.set_level(10)
    workspace = workspace_kant
    input_files = workspace.mets.find_all_files(fileGrp='OCR-D-GT-PAGE')
    input_pcgts0 = page_from_file(input_files[0])
    proc = run_processor(ShellProcessor,
                         workspace=workspace,
                         input_file_grp="OCR-D-GT-PAGE",
                         output_file_grp="OCR-D-OUT",
                         parameter={'command': '''(
echo 'import xml.etree.ElementTree' 
echo 'xml.etree.ElementTree.register_namespace("pc", "http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15")'
echo 'xml.etree.ElementTree.parse("@INFILE").write("@OUTFILE")'
) | python -'''},
                         log_level='DEBUG')
    assert len(caplog.records) > 1
    assert any(rec.message.startswith("Executing processor 'ocrd-command' took")
               for rec in caplog.records
               if rec.name == 'ocrd.process.profile')
    assert sum(1 for rec in caplog.records
               if rec.name == 'ocrd.processor.ShellProcessor' and
               "returned: 0" in rec.message) == 2
    output_files = workspace.mets.find_all_files(fileGrp='OCR-D-OUT')
    assert len(input_files) == len(output_files)
    output_files.sort(key=lambda x: x.url)
    assert output_files[0].local_filename == 'OCR-D-OUT/OCR-D-OUT_PHYS_0017.xml'
    output_pcgts0 = page_from_file(output_files[0])
    assert output_pcgts0.pcGtsId == output_files[0].ID
    assert len(output_pcgts0.Page.get_AllTextLines()) == len(input_pcgts0.Page.get_AllTextLines())

XSLT = '''
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:pc="http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15">
<xsl:output method="xml" version="1.0" omit-xml-declaration="yes" encoding="UTF-8" indent="yes"/>

<xsl:template match="*">
  <xsl:if test="not(starts-with(namespace-uri(),'http://schema.primaresearch.org/PAGE/gts/pagecontent/'))">
    <xsl:message terminate="yes">
      <xsl:text>input document is not of type http://schema.primaresearch.org/PAGE/gts/pagecontent, but </xsl:text>
      <xsl:value-of select="namespace-uri()"/>
    </xsl:message>
  </xsl:if>
  <xsl:element name="pc:{local-name()}">
    <xsl:apply-templates select="@*|node()|text()"/>
  </xsl:element>
</xsl:template>
<xsl:template match="@*|text()">
  <xsl:copy>
    <xsl:apply-templates select="node()|@*|text()"/>
  </xsl:copy>
 </xsl:template>
</xsl:stylesheet>
'''

def test_xslt_command(workspace_kant, caplog):
    caplog.set_level(10)
    workspace = workspace_kant
    input_files = workspace.mets.find_all_files(fileGrp='OCR-D-GT-PAGE')
    input_pcgts0 = page_from_file(input_files[0])
    assert not input_pcgts0.ns_prefix_
    with open("page-add-nsprefix-pc.xslt", "w") as f:
        f.write(XSLT)
    proc = run_processor(ShellProcessor,
                         workspace=workspace,
                         input_file_grp="OCR-D-GT-PAGE",
                         output_file_grp="OCR-D-OUT",
                         parameter={'command': '''(
echo 'import lxml.etree as ET' 
echo 'xslt = ET.parse("page-add-nsprefix-pc.xslt")'
echo 'page = ET.parse("@INFILE")'
echo 'page = ET.XSLT(xslt)(page)'
echo 'print(ET.tostring(page, pretty_print=True, encoding="unicode"))'
) | python - > @OUTFILE'''},
                         log_level='DEBUG')
    
    assert len(caplog.records) > 1
    assert any(rec.message.startswith("Executing processor 'ocrd-command' took")
               for rec in caplog.records
               if rec.name == 'ocrd.process.profile')
    assert sum(1 for rec in caplog.records
               if rec.name == 'ocrd.processor.ShellProcessor' and
               "returned: 0" in rec.message) == 2
    output_files = workspace.mets.find_all_files(fileGrp='OCR-D-OUT')
    assert len(input_files) == len(output_files)
    output_files.sort(key=lambda x: x.url)
    assert output_files[0].local_filename == 'OCR-D-OUT/OCR-D-OUT_PHYS_0017.xml'
    output_pcgts0 = page_from_file(output_files[0])
    assert output_pcgts0.pcGtsId == output_files[0].ID
    assert output_pcgts0.ns_prefix_ == 'pc'
    
if __name__ == "__main__":
    main(__file__)
