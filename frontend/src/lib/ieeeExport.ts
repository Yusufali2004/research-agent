import { 
  Document, 
  Packer, 
  Paragraph, 
  TextRun, 
  AlignmentType, 
  SectionType, 
  convertInchesToTwip,
  Table,
  TableRow,
  TableCell,
  WidthType,
  BorderStyle
} from "docx";
import { saveAs } from "file-saver";

export async function generateIEEEDocx(paper: Record<string, any> | null) {
  if (!paper) {
    alert("Paper data is missing. Please generate the paper first.");
    return;
  }

  try {
    console.log("Starting DOCX generation with data:", paper);

    // 1. SAFELY EXTRACT STRINGS
    const safeString = (val: any, fallback: string) => typeof val === "string" ? val.trim() : fallback;

    const title = safeString(paper.Title, "Generated Research Paper");
    const authors = safeString(paper.Authors, "Author Name");
    let abstract = safeString(paper.Abstract, "Abstract—Not provided.");
    let keywords = safeString(paper.Keywords, "Index Terms—None.");

    if (!abstract.startsWith("Abstract")) abstract = `Abstract—${abstract}`;
    if (!keywords.startsWith("Index Terms")) keywords = `Index Terms—${keywords}`;

    const bodySections = Object.entries(paper).filter(
      ([key]) => !["Title", "Abstract", "Keywords", "Authors"].includes(key)
    );

    const createTable = (tableData: string[][]) => {
      return new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        borders: {
          top: { style: BorderStyle.SINGLE, size: 1, color: "000000" },
          bottom: { style: BorderStyle.SINGLE, size: 1, color: "000000" },
          left: { style: BorderStyle.SINGLE, size: 1, color: "000000" },
          right: { style: BorderStyle.SINGLE, size: 1, color: "000000" },
          insideHorizontal: { style: BorderStyle.SINGLE, size: 1, color: "000000" },
          insideVertical: { style: BorderStyle.SINGLE, size: 1, color: "000000" },
        },
        rows: tableData.map((row, rowIndex) => {
          return new TableRow({
            children: row.map((cellText) => {
              return new TableCell({
                margins: { top: 60, bottom: 60, left: 60, right: 60 },
                children: [
                  new Paragraph({
                    alignment: AlignmentType.CENTER,
                    children: [
                      new TextRun({
                        text: cellText || " ",
                        font: "Times New Roman",
                        size: 16,
                        bold: rowIndex === 0,
                      }),
                    ],
                  }),
                ],
              });
            }),
          });
        }),
      });
    };

    const docBody: any[] = [];

    docBody.push(
      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 120 },
        children: [new TextRun({ text: abstract, font: "Times New Roman", size: 18, bold: true })],
      })
    );

    docBody.push(
      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { after: 300 },
        children: [new TextRun({ text: keywords, font: "Times New Roman", size: 18, bold: true })],
      })
    );

    bodySections.forEach(([sectionName, content]) => {
      if (!content || typeof content !== "string") return; 

      const lines = content.split("\n").map((l) => l.trim());
      let tableBuffer: string[] = [];

      const flushTable = () => {
        if (tableBuffer.length === 0) return;

        const cleanedData: string[][] = [];
        tableBuffer.forEach((tLine) => {
          if (tLine.replace(/[|\-\s]/g, "") === "") return;
          const row = tLine.split("|").slice(1, -1).map((cell) => cell.trim());
          if (row.length > 0) cleanedData.push(row);
        });

        if (cleanedData.length > 0) {
          docBody.push(createTable(cleanedData));
          docBody.push(new Paragraph({ spacing: { after: 200 } }));
        }
        tableBuffer = [];
      };

      lines.forEach((line, index) => {
        if (line.startsWith("|") && line.endsWith("|")) {
          tableBuffer.push(line);
          return;
        } else {
          flushTable();
        }

        if (!line) return;

        const imgMatch = line.match(/\[IMAGE:\s*(.+?)\]/i);
        if (imgMatch) {
          docBody.push(
            new Paragraph({
              alignment: AlignmentType.CENTER,
              spacing: { before: 120, after: 120 },
              children: [
                new TextRun({
                  text: `[ Insert Image Here: ${imgMatch[1]} ]`,
                  font: "Times New Roman",
                  size: 20,
                  italics: true,
                  color: "888888", 
                }),
              ],
            })
          );
          line = line.replace(/\[IMAGE:\s*(.+?)\]/ig, "").trim();
          if (!line) return;
        }

        if (line.startsWith("Fig.") || line.startsWith("[Fig.") || line.startsWith("Table")) {
          docBody.push(
            new Paragraph({
              alignment: AlignmentType.CENTER,
              spacing: { before: 120, after: 240 },
              children: [new TextRun({ text: line, font: "Times New Roman", size: 16, color: "00008B" })],
            })
          );
        } else if (
          (index === 0 && line.match(/^[I|V|X]+\./)) ||
          line.toUpperCase() === "ACKNOWLEDGMENT" ||
          line.toUpperCase() === "REFERENCES"
        ) {
          docBody.push(
            new Paragraph({
              alignment: AlignmentType.CENTER,
              spacing: { before: 240, after: 120 },
              children: [new TextRun({ text: line.toUpperCase(), font: "Times New Roman", size: 20 })],
            })
          );
        } else if (line.match(/^[A-Z]\./)) {
          docBody.push(
            new Paragraph({
              alignment: AlignmentType.LEFT,
              spacing: { before: 120, after: 60 },
              children: [new TextRun({ text: line, font: "Times New Roman", size: 20, italics: true })],
            })
          );
        } else if (line.startsWith("[")) {
          docBody.push(
            new Paragraph({
              alignment: AlignmentType.JUSTIFIED,
              spacing: { after: 60 },
              children: [new TextRun({ text: line, font: "Times New Roman", size: 16 })],
            })
          );
        } else {
          docBody.push(
            new Paragraph({
              alignment: AlignmentType.JUSTIFIED,
              spacing: { after: 0, line: 240 }, 
              children: [new TextRun({ text: line, font: "Times New Roman", size: 20 })],
            })
          );
        }
      });

      flushTable();
    });

    if (docBody.length === 0) {
      docBody.push(new Paragraph({ text: "No content extracted." }));
    }

    const doc = new Document({
      sections: [
        {
          properties: {
            type: SectionType.CONTINUOUS,
            page: {
              margin: {
                top: convertInchesToTwip(1),
                right: convertInchesToTwip(0.75),
                bottom: convertInchesToTwip(1),
                left: convertInchesToTwip(0.75),
              },
            },
          },
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              spacing: { after: 200 },
              children: [new TextRun({ text: title, font: "Times New Roman", size: 48 })],
            }),
            new Paragraph({
              alignment: AlignmentType.CENTER,
              spacing: { after: 400 },
              children: [new TextRun({ text: authors, font: "Times New Roman", size: 22 })],
            }),
          ],
        },
        {
          properties: {
            type: SectionType.CONTINUOUS,
            column: { space: convertInchesToTwip(0.2), count: 2 },
          },
          children: docBody,
        },
      ],
    });

    const blob = await Packer.toBlob(doc);
    saveAs(blob, "IEEE_Research_Paper.docx");
    
  } catch (error) {
    console.error("DOCX generation critical failure:", error);
    alert("DOCX Export failed. Check the console for details.");
  }
}