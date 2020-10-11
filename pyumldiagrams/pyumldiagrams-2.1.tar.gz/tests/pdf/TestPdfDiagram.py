from typing import List
from typing import cast


from logging import Logger
from logging import getLogger

from unittest import TestSuite
from unittest import main as unitTestMain

from pyumldiagrams.Definitions import ClassDefinition
from pyumldiagrams.Definitions import ClassDefinitions
from pyumldiagrams.Definitions import DefinitionType
from pyumldiagrams.Definitions import LinePositions
from pyumldiagrams.Definitions import UmlLineDefinition
from pyumldiagrams.Definitions import UmlLineDefinitions
from pyumldiagrams.Definitions import LineType
from pyumldiagrams.Definitions import MethodDefinition
from pyumldiagrams.Definitions import ParameterDefinition
from pyumldiagrams.Definitions import Position
from pyumldiagrams.Definitions import Size

from pyumldiagrams.pdf.PdfDiagram import PdfDiagram
from pyumldiagrams.xmlsupport.ToClassDefinition import ToClassDefinition

from tests.TestBase import TestBase

from tests.TestConstants import TestConstants
from tests.TestDiagramParent import TestDiagramParent


class TestPdfDiagram(TestDiagramParent):
    """
    The following all test with the default horizontal/vertical gaps and the default top/left margins
    """

    TEST_LAST_X_POSITION: int = 9
    TEST_LAST_Y_POSITION: int = 6

    CELL_WIDTH:  int = 150  # points
    CELL_HEIGHT: int = 100  # points

    clsLogger: Logger = None

    @classmethod
    def setUpClass(cls):
        TestBase.setUpLogging()
        TestPdfDiagram.clsLogger = getLogger(__name__)

    def setUp(self):
        self.logger: Logger = TestPdfDiagram.clsLogger

    def tearDown(self):
        pass

    def testConstruction(self):

        diagram: PdfDiagram = PdfDiagram(fileName=TestConstants.TEST_FILE_NAME, dpi=TestConstants.TEST_DPI)
        self.assertIsNotNone(diagram, 'Construction failed')

        self.assertEqual(PdfDiagram.DEFAULT_FONT_SIZE, diagram.fontSize, 'Default font size changed')

    def testBuildMethod(self):

        diagram: PdfDiagram = PdfDiagram(fileName=cast(str, None), dpi=cast(int, None))

        initMethodDef: MethodDefinition = self._buildInitMethod()

        actualRepr:    str = diagram._buildMethod(initMethodDef)
        expectedRepr:  str = '+ __init__(make: str, model: str, year: int=1957)'

        self.assertEqual(expectedRepr, actualRepr, 'Method building is incorrect')

    def testBuildMethods(self):

        diagram: PdfDiagram = PdfDiagram(fileName=cast(str, None), dpi=cast(int, None))

        car: ClassDefinition = self._buildCar()

        reprs: PdfDiagram.MethodsRepr = diagram._buildMethods(car.methods)

        self.assertEqual(5, len(reprs), 'Generated incorrect number of method representations')

    def testBasicDiagramDraw(self):

        diagram: PdfDiagram = PdfDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-Basic{TestConstants.TEST_SUFFIX}', dpi=TestConstants.TEST_DPI)
        classDef: ClassDefinition = ClassDefinition(name=TestDiagramParent.BASE_TEST_CLASS_NAME,
                                                    size=Size(width=TestPdfDiagram.CELL_WIDTH, height=TestPdfDiagram.CELL_HEIGHT))

        diagram.drawClass(classDef)
        diagram.write()

    def testFillPage(self):

        diagram: PdfDiagram = PdfDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-Full{TestConstants.TEST_SUFFIX}', dpi=TestConstants.TEST_DPI)

        widthInterval:  int = TestPdfDiagram.CELL_WIDTH // 10
        heightInterval: int = TestPdfDiagram.CELL_HEIGHT // 10

        for x in range(0, TestPdfDiagram.TEST_LAST_X_POSITION):
            scrX: int = (x * TestPdfDiagram.CELL_WIDTH) + (widthInterval * x)

            for y in range(0, TestPdfDiagram.TEST_LAST_Y_POSITION):

                scrY: int = (y * TestPdfDiagram.CELL_HEIGHT) + (y * heightInterval)
                classDef: ClassDefinition = ClassDefinition(name=f'{TestPdfDiagram.BASE_TEST_CLASS_NAME}{x}{y}',
                                                            position=Position(scrX, scrY),
                                                            size=Size(width=TestPdfDiagram.CELL_WIDTH, height=TestPdfDiagram.CELL_HEIGHT))
                diagram.drawClass(classDef)

        diagram.write()

    def testBasicMethod(self):

        diagram: PdfDiagram = PdfDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-BasicMethod{TestConstants.TEST_SUFFIX}', dpi=TestConstants.TEST_DPI)

        position: Position = Position(107, 30)
        size:     Size     = Size(width=266, height=100)

        car: ClassDefinition = ClassDefinition(name='Car', position=position, size=size)

        initMethodDef: MethodDefinition = MethodDefinition(name='__init__', visibility=DefinitionType.Public)

        initParam: ParameterDefinition = ParameterDefinition(name='make', parameterType='str', defaultValue='')
        initMethodDef.parameters = [initParam]
        car.methods = [initMethodDef]

        diagram.drawClass(car)

        diagram.write()

    def testBasicMethods(self):

        diagram: PdfDiagram = PdfDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-BasicMethods{TestConstants.TEST_SUFFIX}', dpi=TestConstants.TEST_DPI)

        classDef: ClassDefinition = self._buildCar()

        diagram.drawClass(classDef)

        diagram.write()

    def testBasicHeader(self):

        diagram: PdfDiagram = PdfDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-BasicHeader{TestConstants.TEST_SUFFIX}',
                                         dpi=TestConstants.TEST_DPI,
                                         headerText=TestDiagramParent.UNIT_TEST_HEADER)
        classDef: ClassDefinition = self._buildCar()

        diagram.drawClass(classDef)

        diagram.write()

    def testSophisticatedHeader(self):
        from time import localtime

        from time import strftime

        today = strftime("%d %b %Y %H:%M:%S", localtime())

        diagram: PdfDiagram = PdfDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-SophisticatedHeader{TestConstants.TEST_SUFFIX}',
                                         dpi=TestConstants.TEST_DPI,
                                         headerText=f'{TestDiagramParent.UNIT_TEST_SOPHISTICATED_HEADER} - {today}')
        classDef: ClassDefinition = self._buildCar()

        diagram.drawClass(classDef)

        diagram.write()

    def testSophisticatedLayout(self):

        diagram: PdfDiagram = PdfDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-SophisticatedLayout{TestConstants.TEST_SUFFIX}', dpi=TestConstants.TEST_DPI)

        classDefinitions: ClassDefinitions = [
            self._buildCar(),
            self._buildCat(),
            self._buildOpie(),
            self._buildNameTestCase(),
            self._buildElectricCar()
        ]
        for classDefinition in classDefinitions:
            classDefinition = cast(ClassDefinition, classDefinition)
            diagram.drawClass(classDefinition=classDefinition)

        lineDefinitions: UmlLineDefinitions = self._buildSophisticatedLineDefinitions()
        for lineDefinition in lineDefinitions:
            diagram.drawUmlLine(lineDefinition=lineDefinition)

        diagram.write()

    def testMinimalInheritance(self):

        diagram: PdfDiagram = PdfDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-MinimalInheritance{TestConstants.TEST_SUFFIX}', dpi=75)

        cat:  ClassDefinition = ClassDefinition(name='Gato', position=Position(536, 19), size=Size(height=74, width=113))
        opie: ClassDefinition = ClassDefinition(name='Opie', position=Position(495, 208), size=Size(width=216, height=87))

        diagram.drawClass(classDefinition=cat)
        diagram.drawClass(classDefinition=opie)

        linePositions: LinePositions = [Position(600, 208), Position(600, 93)]
        opieToCat: UmlLineDefinition = UmlLineDefinition(lineType=LineType.Inheritance, linePositions=linePositions)

        diagram.drawUmlLine(lineDefinition=opieToCat)
        diagram.write()

    def testMethodReprRegression(self):

        testFileName: str = f'{TestConstants.TEST_FILE_NAME}-BasicMethodRegression{TestConstants.TEST_SUFFIX}'
        diagram: PdfDiagram = PdfDiagram(fileName=testFileName, dpi=TestConstants.TEST_DPI)

        position: Position = Position(107, 30)
        size:     Size     = Size(width=266, height=100)

        car: ClassDefinition = ClassDefinition(name='Car', position=position, size=size)

        #
        # Make visibility None
        initMethodDef: MethodDefinition = MethodDefinition(name='__init__', visibility=cast(DefinitionType, None))

        car.methods = [initMethodDef]

        diagram.drawClass(car)

        diagram.write()

    def testBasicFields(self):

        fileName: str        = f'{TestConstants.TEST_FILE_NAME}-BasicFields{TestConstants.TEST_SUFFIX}'
        diagram:  PdfDiagram = PdfDiagram(fileName=fileName, dpi=TestConstants.TEST_DPI)

        fieldsTestClass: ClassDefinition = ClassDefinition(name='FieldsTestClass', position=Position(226, 102), size=Size(height=156, width=230))

        fieldsTestClass.fields = self._buildFields()

        initMethodDef: MethodDefinition = MethodDefinition(name='__init__', visibility=DefinitionType.Public)

        fieldsTestClass.methods = [initMethodDef]

        diagram.drawClass(classDefinition=fieldsTestClass)

        diagram.write()

    def testBends(self):
        fileName: str        = f'{TestConstants.TEST_FILE_NAME}-Bends{TestConstants.TEST_SUFFIX}'
        diagram:  PdfDiagram = PdfDiagram(fileName=fileName, dpi=TestConstants.TEST_DPI)

        top:   ClassDefinition = self._buildTopClass()
        left:  ClassDefinition = self._buildLeftClass()
        right: ClassDefinition = self._buildRightClass()

        bentClasses: List[ClassDefinition] = [top, left, right]
        for bentClass in bentClasses:
            diagram.drawClass(classDefinition=bentClass)

        bentLineDefinitions: UmlLineDefinitions = self._buildBendTest()

        for bentLine in bentLineDefinitions:
            diagram.drawUmlLine(bentLine)

        diagram.write()

    def testBendsFromXmlInput(self):

        toClassDefinition: ToClassDefinition = self._buildBendTestFromXml()

        fileName: str        = f'{TestConstants.TEST_FILE_NAME}-BendsFromXmlInput{TestConstants.TEST_SUFFIX}'
        diagram:  PdfDiagram = PdfDiagram(fileName=fileName, dpi=TestConstants.TEST_DPI)

        classDefinitions: ClassDefinitions = toClassDefinition.classDefinitions
        for bentClass in classDefinitions:
            diagram.drawClass(classDefinition=bentClass)

        bentLineDefinitions: UmlLineDefinitions = toClassDefinition.umlLineDefinitions

        for bentLine in bentLineDefinitions:
            diagram.drawUmlLine(bentLine)

        diagram.write()

    def testBigClass(self):

        toClassDefinition: ToClassDefinition = self._buildBigClassFromXml()
        fileName: str        = f'{TestConstants.TEST_FILE_NAME}-BigClass{TestConstants.TEST_SUFFIX}'
        diagram:  PdfDiagram = PdfDiagram(fileName=fileName, dpi=TestConstants.TEST_DPI)

        classDefinitions: ClassDefinitions = toClassDefinition.classDefinitions
        for bigClass in classDefinitions:
            diagram.drawClass(classDefinition=bigClass)

        diagram.write()


def suite() -> TestSuite:
    """You need to change the name of the test class here also."""
    import unittest

    testSuite: TestSuite = TestSuite()
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestPdfDiagram))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
