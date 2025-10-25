from docxtpl import DocxTemplate

doc = DocxTemplate("docact.docx")
print(doc.get_undeclared_template_variables())