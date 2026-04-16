from flask import Flask, render_template, request, send_file, jsonify
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
import io
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.get_json()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle('InvoiceTitle', fontSize=28, fontName='Helvetica-Bold',
                                  textColor=colors.HexColor('#111111'), spaceAfter=4)
    label_style = ParagraphStyle('Label', fontSize=9, fontName='Helvetica',
                                  textColor=colors.HexColor('#999999'), spaceAfter=3,
                                  leading=12)
    name_style = ParagraphStyle('Name', fontSize=13, fontName='Helvetica-Bold',
                                 textColor=colors.HexColor('#111111'), spaceAfter=2)
    detail_style = ParagraphStyle('Detail', fontSize=10, fontName='Helvetica',
                                   textColor=colors.HexColor('#666666'), leading=14)
    right_style = ParagraphStyle('Right', fontSize=10, fontName='Helvetica',
                                  textColor=colors.HexColor('#666666'), alignment=TA_RIGHT)
    notes_style = ParagraphStyle('Notes', fontSize=10, fontName='Helvetica',
                                  textColor=colors.HexColor('#888888'), leading=14)

    biz = data.get('business', {})
    client = data.get('client', {})
    invoice = data.get('invoice', {})
    items = data.get('items', [])
    tax_rate = float(data.get('tax_rate', 0))
    notes = data.get('notes', '')

    # Header row: INVOICE title left, invoice number/status right
    inv_num = invoice.get('number', 'INV-001')
    inv_date = invoice.get('date', '')
    due_date = invoice.get('due_date', '')

    header_data = [
        [Paragraph('Invoice', title_style),
         Paragraph(f'<font color="#999999" size="10">{inv_num}</font><br/>'
                   f'<font color="#999999" size="9">Issued: {inv_date}</font><br/>'
                   f'<font color="#999999" size="9">Due: {due_date}</font>', right_style)]
    ]
    header_table = Table(header_data, colWidths=[4*inch, 2.5*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#eeeeee'), spaceAfter=14, spaceBefore=10))

    # From / Bill To
    biz_detail = f"{biz.get('address','').replace(chr(10),'<br/>')}<br/>{biz.get('email','')}&nbsp;&nbsp;{biz.get('phone','')}"
    cl_detail = f"{client.get('address','').replace(chr(10),'<br/>')}<br/>{client.get('email','')}"

    parties_data = [
        [Paragraph('FROM', label_style), Paragraph('BILL TO', label_style)],
        [Paragraph(biz.get('name','Your Business'), name_style), Paragraph(client.get('name','Client'), name_style)],
        [Paragraph(biz_detail, detail_style), Paragraph(cl_detail, detail_style)],
    ]
    parties_table = Table(parties_data, colWidths=[3.25*inch, 3.25*inch])
    parties_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(parties_table)
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#eeeeee'), spaceAfter=10, spaceBefore=14))

    # Line items table
    th_style = ParagraphStyle('TH', fontSize=9, fontName='Helvetica-Bold',
                               textColor=colors.HexColor('#999999'))
    td_style = ParagraphStyle('TD', fontSize=10, fontName='Helvetica',
                               textColor=colors.HexColor('#111111'))
    td_right = ParagraphStyle('TDR', fontSize=10, fontName='Helvetica',
                               textColor=colors.HexColor('#111111'), alignment=TA_RIGHT)

    table_data = [[
        Paragraph('DESCRIPTION', th_style),
        Paragraph('QTY', th_style),
        Paragraph('UNIT PRICE', th_style),
        Paragraph('AMOUNT', th_style),
    ]]

    subtotal = 0
    for item in items:
        qty = float(item.get('qty', 1))
        price = float(item.get('price', 0))
        amount = qty * price
        subtotal += amount
        table_data.append([
            Paragraph(item.get('desc', ''), td_style),
            Paragraph(str(int(qty) if qty == int(qty) else qty), td_right),
            Paragraph(f'${price:,.2f}', td_right),
            Paragraph(f'${amount:,.2f}', td_right),
        ])

    items_table = Table(table_data, colWidths=[3.3*inch, 0.8*inch, 1.1*inch, 1.3*inch])
    items_table.setStyle(TableStyle([
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,0), 0.5, colors.HexColor('#dddddd')),
        ('LINEBELOW', (0,1), (-1,-1), 0.3, colors.HexColor('#f0f0f0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 10))

    # Totals
    tax_amt = subtotal * tax_rate / 100
    total = subtotal + tax_amt

    totals_right = ParagraphStyle('TotR', fontSize=11, fontName='Helvetica',
                                   textColor=colors.HexColor('#666666'), alignment=TA_RIGHT)
    totals_right_bold = ParagraphStyle('TotRB', fontSize=13, fontName='Helvetica-Bold',
                                        textColor=colors.HexColor('#111111'), alignment=TA_RIGHT)
    totals_label = ParagraphStyle('TotL', fontSize=11, fontName='Helvetica',
                                   textColor=colors.HexColor('#666666'), alignment=TA_RIGHT)
    totals_label_bold = ParagraphStyle('TotLB', fontSize=13, fontName='Helvetica-Bold',
                                        textColor=colors.HexColor('#111111'), alignment=TA_RIGHT)

    totals_data = [
        [Paragraph('Subtotal', totals_label), Paragraph(f'${subtotal:,.2f}', totals_right)],
        [Paragraph(f'Tax ({tax_rate:.1f}%)', totals_label), Paragraph(f'${tax_amt:,.2f}', totals_right)],
        [Paragraph('Total Due', totals_label_bold), Paragraph(f'${total:,.2f}', totals_right_bold)],
    ]
    totals_table = Table(totals_data, colWidths=[5.5*inch, 1.0*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('LINEABOVE', (0,2), (-1,2), 0.5, colors.HexColor('#dddddd')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,2), (-1,2), 8),
    ]))
    story.append(totals_table)

    if notes:
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#eeeeee'), spaceAfter=8, spaceBefore=14))
        story.append(Paragraph(notes, notes_style))

    doc.build(story)
    buffer.seek(0)

    filename = f"invoice-{inv_num}.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
