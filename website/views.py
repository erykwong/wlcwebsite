from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse
from django.db.models import Sum
from django.views.generic import ListView, UpdateView, CreateView, DeleteView, DetailView, TemplateView
from .models import Matter, Lawyer, Client, Service, Disbursement, Discount

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT, TA_JUSTIFY


class HomeView(TemplateView):
    template_name = 'website/index.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        return context


def generate_invoice(request, matter_id):
    # Generate PDF by following template
    # Trust - Services - Disbursement = outstanding
    # Discounts are applied before disbursements
    # Discounts that are percentage based are applied before flat ones
    # Taxable disbursements adds a 12% cost on that disbursement

    '''
    doc = SimpleDocTemplate("test.pdf", pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)

    Story = []
    services = Service.objects.filter(matter=matter_id)
    disbursements = Disbursement.objects.filter(matter=matter_id)
    discounts = Discount.objects.filter(matter=matter_id)

    Story = [Spacer(1, 2 * inch)]
    styles = getSampleStyleSheet()
    style = styles["Normal"]

    doc.build(Story)

    with open("test.pdf") as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="/invoices/test.pdf"'
        return response
    '''

    from io import BytesIO
    from reportlab.pdfgen import canvas
    from datetime import timedelta
    from decimal import Decimal

    # Invoice information
    matter = Matter.objects.get(id=matter_id)
    gst = "802875021RT001"
    gst_percentage = 0.05
    pst = "1017-6415"
    pst_percentage = 0.07

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="' + matter.invoice_number + '".pdf"'

    buffer = BytesIO()

    # Create the PDF object, using the BytesIO object as its "file."
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=15, bottomMargin=15)
    styles = getSampleStyleSheet()
    style_left = ParagraphStyle(name='left', parent=styles['Normal'], alignment=TA_LEFT)
    style_right = ParagraphStyle(name='right', parent=styles['Normal'], alignment=TA_RIGHT)
    style_justify = ParagraphStyle(name='justify', parent=styles['Normal'], alignment=TA_JUSTIFY)
    style_center = ParagraphStyle(name='center', parent=styles['Normal'], alignment=TA_CENTER)
    Story = []

    # Logo
    logo = "website/static/website/images/logo.png"
    im = Image(logo, 2*inch, 2*inch, hAlign='LEFT')

    # Company Information Header
    company_name = "<b>WINRIGHT LAW CORPORATION</b>"
    company_info = ["621 - 550 West Broadway | Vancouver, BC | V5Z 0E9",
                    "t: 604.559.2529 f: 604.559.2530",
                    "info@wrlaw.ca | winrightlaw.com"]
    company_header = []
    p_text = '<font size=12>%s</font>' % company_name
    company_header.append(Paragraph(p_text, style_right))
    for info in company_info:
        p_text = '<font size=12>%s</font>' % info
        company_header.append(Paragraph(p_text, style_right))

    header_data = [
        [im, company_header]
    ]

    tbl_header = Table(header_data, colWidths=[280, 300])
    tbl_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    Story.append(tbl_header)

    # Invoice and Client Information
    #  File and Invoice Number
    file_num_text = Paragraph('<font size=12><b>%s</b></font' % 'File #: ', style_left)
    file_num_data = Paragraph('<font size=12>%s</font' % matter.file_number, style_left)
    invoice_num_text = Paragraph('<font size=12><b>%s</b></font' % 'Invoice #: ', style_left)
    invoice_num_data = Paragraph('<font size=12>%s</font' % matter.invoice_number, style_left)

    #  Date
    date_text = Paragraph('<font size=12>%s</font' % 'Date: ', style_left)
    date_data = Paragraph('<font size=12>%s</font' % matter.invoice_date.strftime("%m/%d/%y"), style_left)
    due_date_text = Paragraph('<font size=12>%s</font' % 'Due On: ', style_left)
    due_date = (matter.invoice_date + timedelta(days=30)).strftime("%m/%d/%y")
    due_date_data = Paragraph('<font size=12>%s</font' % due_date, style_left)

    #  Client Information
    client_company = Paragraph('<font size=12><b>%s</b></font>' % matter.client.name, style_left)
    address_line_1 = Paragraph('<font size=12>%s</font>' % matter.client.address.address_line_1, style_left)
    address_line_2 = Paragraph('<font size=12>%s</font>' % matter.client.address.address_line_2, style_left)
    address_line_3 = Paragraph('<font size=12>%s</font>' % matter.client.address.address_line_3, style_left)

    #  Tax Information
    gst_text = Paragraph('<font size=12>%s</font' % 'GST: ', style_left)
    gst_data = Paragraph('<font size=12>%s</font' % gst, style_left)
    pst_text = Paragraph('<font size=12>%s</font' % 'PST: ', style_left)
    pst_data = Paragraph('<font size=12>%s</font' % pst, style_left)

    invoice_data = [
        [Paragraph('<font size=14><b>%s</b></font' % 'INVOICE', style_left)],
        [file_num_text, file_num_data, date_text, date_data],
        [invoice_num_text, invoice_num_data, due_date_text, due_date_data],
    ]
    tbl_invoice = Table(invoice_data, colWidths=[95, 230, 100, 140])
    Story.append(tbl_invoice)
    Story.append(Spacer(1, 12))

    client_tax_data = [
        [client_company, gst_text, gst_data],
        [address_line_1, pst_text, pst_data],
        [address_line_2],
        [address_line_3]
    ]

    tbl_client_tax = Table(client_tax_data, colWidths=[330, 100, 140])
    Story.append(tbl_client_tax)
    Story.append(Spacer(1, 12))

    # Matter fees, discounts and disbursements
    Story.append(Paragraph('<font size=12>%s</font>' % matter.summary, style_left))

    # Draw line
    line = Drawing(100, 1)
    line.add(Line(0, 0, 550, 0))
    Story.append(line)
    Story.append(Spacer(1, 12))

    date_heading_text = Paragraph('<font size=12><b>%s</b></font' % 'DATE', style_left)
    desc_heading_text = Paragraph('<font size=12><b>%s</b></font' % 'DESCRIPTION', style_left)
    amt_heading_text = Paragraph('<font size=12><b>%s</b></font' % 'AMOUNT', style_left)
    lawyer_heading_text = Paragraph('<font size=12><b>%s</b></font' % 'LAWYER', style_left)

    # Services
    services_header = Paragraph('<font size=12><b>%s</b></font>' % 'SERVICES', style_left)
    Story.append(services_header)

    services_data = [
        [date_heading_text, desc_heading_text, amt_heading_text, lawyer_heading_text]
    ]

    total_service_cost = 0
    services = Service.objects.filter(matter_id=matter_id)
    for service in services:
        total_service_cost += service.amount

        service_date = Paragraph('<font size=12>%s</font>' % service.date.strftime("%m/%d/%y"), style_left)
        service_desc = Paragraph('<font size=12>%s</font>' % service.description, style_left)
        service_amt = Paragraph('<font size=12>%s</font>' % str(service.amount), style_right)
        lawyer = Paragraph('<font size=12>%s</font>' % service.lawyer.name, style_left)
        services_data.append([service_date, service_desc, service_amt, lawyer])

    fee_total_text = Paragraph('<font size=12><b>%s</b></font' % 'Fee Total: ', style_right)
    gst_fee_text = Paragraph('<font size=12>%s</font' % 'GST on Fees: ', style_right)
    pst_fee_text = Paragraph('<font size=12>%s</font' % 'PST on Fees: ', style_right)
    fee_total_with_taxes_text = Paragraph('<font size=12><b>%s</b></font' % 'Fee Total with Taxes: ', style_right)

    gst_fee = total_service_cost * Decimal(gst_percentage)
    pst_fee = total_service_cost * Decimal(pst_percentage)
    total_cost_with_fee = total_service_cost + gst_fee + pst_fee

    service_cost = Paragraph('<font size=12>%s</font' % str(total_service_cost), style_right)
    gst_cost = Paragraph('<font size=12>%s</font' % str(format(gst_fee, '.2f')), style_right)
    pst_cost = Paragraph('<font size=12>%s</font' % str(format(pst_fee, '.2f')), style_right)
    total_cost = Paragraph('<font size=12>%s</font' % str(format(total_cost_with_fee, '.2f')), style_right)

    services_data.append(["", fee_total_text, service_cost, ""])
    services_data.append(["", gst_fee_text, gst_cost, ""])
    services_data.append(["", pst_fee_text, pst_cost, ""])
    services_data.append(["", fee_total_with_taxes_text, total_cost, ""])

    tbl_service = Table(services_data, colWidths=[95, 300, 70, 100])
    Story.append(tbl_service)
    Story.append(Spacer(1, 12))

    # Discounts
    discounts_header = Paragraph('<font size=12><b>%s</b></font>' % 'DISCOUNTS', style_left)
    Story.append(discounts_header)

    date_heading_text = Paragraph('<font size=12><b>%s</b></font' % 'DATE', style_left)
    desc_heading_text = Paragraph('<font size=12><b>%s</b></font' % 'DESCRIPTION', style_left)
    amt_heading_text = Paragraph('<font size=12><b>%s</b></font' % 'AMOUNT', style_left)
    discount_heading_text = Paragraph('<font size=12><b>%s</b></font' % 'DISCOUNT', style_left)

    disc_data = [
        [date_heading_text, desc_heading_text, amt_heading_text, discount_heading_text]
    ]

    discounts = Discount.objects.filter(matter_id=matter_id)
    total_percentage_discount = 0
    total_flat_discount = 0
    for discount in discounts:
        if discount.discount_choice == "Percentage":
            total_percentage_discount += discount.amount
        elif discount.discount_choice == "Flat":
            total_flat_discount += discount.amount

        discount_date = Paragraph('<font size=12>%s</font>' % discount.date.strftime("%m/%d/%y"), style_left)
        discount_name = Paragraph('<font size=12>%s</font>' % discount.name, style_left)
        discount_amt = Paragraph('<font size=12>%s</font>' % str(discount.amount), style_right)
        discount_type = Paragraph('<font size=12>%s</font>' % discount.discount_choice, style_left)
        disc_data.append([discount_date, discount_name, discount_amt, discount_type])

    percentage_off = total_cost_with_fee * (total_percentage_discount / 100)
    cost_after_discounts = total_cost_with_fee - percentage_off - total_flat_discount

    discount_percentage_text = Paragraph('<font size=12>%s</font' % 'Percent Discount:', style_right)
    discount_flat_text = Paragraph('<font size=12>%s</font' % 'Flat Discount:', style_right)
    total_after_text = Paragraph('<font size=12><b>%s</b></font' % 'Cost After Discount:', style_right)

    discount_percentage = Paragraph('<font size=12>%s</font' % str(total_percentage_discount), style_right)
    discount_flat = Paragraph('<font size=12>%s</font' % str(total_flat_discount), style_right)
    total_after_discount = Paragraph('<font size=12>%s</font' % str(format(cost_after_discounts, '.2f')), style_right)

    disc_data.append(["", discount_percentage_text, discount_percentage, ""])
    disc_data.append(["", discount_flat_text, discount_flat, ""])
    disc_data.append(["", total_after_text, total_after_discount, ""])

    tbl_disc = Table(disc_data, colWidths=[95, 300, 70, 100])
    Story.append(tbl_disc)
    Story.append(Spacer(1, 12))

    # Disbursements
    disbursement_header = Paragraph('<font size=12><b>%s</b></font>' % 'DISBURSEMENTS', style_left)
    Story.append(disbursement_header)

    date_heading_text = Paragraph('<font size=12><b>%s</b></font' % 'DATE', style_left)
    desc_heading_text = Paragraph('<font size=12><b>%s</b></font' % 'DESCRIPTION', style_left)
    amt_heading_text = Paragraph('<font size=12><b>%s</b></font' % 'AMOUNT', style_left)
    taxable_heading_text = Paragraph('<font size=12><b>%s</b></font' % 'TAX', style_left)

    disb_data = [
        [date_heading_text, desc_heading_text, amt_heading_text, taxable_heading_text]
    ]

    total_disbursement_cost = 0
    disbursements = Disbursement.objects.filter(matter_id=matter_id)

    for disbursement in disbursements:
        total_disbursement_cost += disbursement.amount
        disb_date = Paragraph('<font size=12>%s</font>' % disbursement.date.strftime("%m/%d/%y"), style_left)
        disb_desc = Paragraph('<font size=12>%s</font>' % disbursement.description, style_left)
        disb_amt = Paragraph('<font size=12>%s</font>' % str(disbursement.amount), style_right)
        disb_tax_choice = Paragraph('<font size=12>%s</font>' % disbursement.tax_choice, style_left)
        disb_data.append([disb_date, disb_desc, disb_amt, disb_tax_choice])

        # TODO Determine if TAX_CHOICE is NON-TAXABLE, TAXABLE(GST+PST), GST only, PST only

    tbl_disb = Table(disb_data, colWidths=[95, 300, 70, 100])
    Story.append(tbl_disb)

    # TODO add calculations
    Story.append(Spacer(1, 12))

    doc.build(Story)

    '''
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setLineWidth(.3)
    p.setFont('Helvetica', 12)

    # Create logo on the top left
    logo = "website/static/website/images/logo.png"
    p.drawImage(logo, 10, 640, 150, 150)

    # Create company information header
    p.setFont('Helvetica-Bold', 12)
    p.drawString(400, 760, "WINRIGHT LAW CORPORATION")
    p.setFont('Helvetica', 12)
    p.line(250, 755, 600, 755)
    p.drawString(300, 740, "621 - 550 West Broadway | Vancouver, BC | V5Z 0E9")
    p.drawString(400, 720, "t: 604.559.2529 f: 604.559.2530")
    p.drawString(400, 700, "info@wrlaw.ca | winrightlaw.com")

    # Left side
    p.setFont('Helvetica-Bold', 12)
    p.drawString(10, 640, "INVOICE")
    p.setFont('Helvetica', 12)
    p.drawString(10, 620, "File #: ")
    p.drawString(80, 620, matter.file_number)

    p.drawString(10, 600, "Invoice #: ")
    p.drawString(80, 600, matter.invoice_number)

    p.setFont('Helvetica-Bold', 12)
    p.drawString(10, 550, matter.client.name)
    p.setFont('Helvetica', 12)
    p.drawString(10, 530, matter.client.address)

    # Right side
    p.drawString(400, 620, "Date: ")
    p.drawString(460, 620, matter.invoice_date.strftime("%m/%d/%y"))
    p.drawString(400, 600, "Due on: ")
    p.drawString(460, 600, (matter.invoice_date + timedelta(days=30)).strftime("%m/%d/%y"))

    p.drawString(400, 550, "GST#: ")
    p.drawString(440, 550, gst)
    p.drawString(400, 530, "PST#: ")
    p.drawString(440, 530, pst)

    # Center area
    p.drawString(10, 480, matter.summary)
    p.line(10, 470, 550, 470)

    # Titles
    titles_y = 430
    p.setFont('Helvetica-Bold', 12)
    p.drawString(10, titles_y, "DATE")
    p.drawString(110, titles_y, "DESCRIPTION")
    p.drawString(450, titles_y, "AMOUNT")
    p.drawString(510, titles_y, "LAWYER")
    p.setFont('Helvetica', 12)

    # Service and Disbursement Alignment Variables
    fee_disb_labels_x = 250

    # Services
    services = Service.objects.filter(matter_id=matter_id)
    y_axis = titles_y
    total_service_cost = 0
    for service in services:
        y_axis -= 20
        p.drawString(10, y_axis, service.date.strftime("%m/%d/%y"))
        p.drawString(110, y_axis, service.description)
        p.drawString(450, y_axis, str(service.amount))
        p.drawString(510, y_axis, service.lawyer.name)
        total_service_cost += service.amount

    # Fee total
    y_axis -= 20
    p.drawString(fee_disb_labels_x, y_axis, "Fee Total")
    p.drawString(450, y_axis, str(total_service_cost))

    # GST on Fees
    y_axis -= 20
    p.drawString(fee_disb_labels_x, y_axis, "GST on Fees")
    gst_fee = total_service_cost * Decimal(gst_percentage)
    p.drawString(fee_disb_labels_x + 200, y_axis, str(format(gst_fee, '.2f')))

    # PST on Fees
    y_axis -= 20
    p.drawString(fee_disb_labels_x, y_axis, "PST on Fees")
    pst_fee = total_service_cost * Decimal(pst_percentage)
    p.drawString(fee_disb_labels_x + 200, y_axis, str(format(pst_fee, '.2f')))

    # Fee Total with Taxes
    p.setFont('Helvetica-Bold', 12)
    y_axis -= 20
    p.drawString(fee_disb_labels_x, y_axis, "Fee Total with Taxes")
    total_fee = total_service_cost + gst_fee + pst_fee
    p.drawString(fee_disb_labels_x + 200, y_axis, str(format(total_fee, '.2f')))
    p.setFont('Helvetica', 12)

    # Discounts

    # TODO ADD DISCOUNTS

    # Disbursements
    y_axis -= 20
    p.setFont('Helvetica-Bold', 12)
    p.drawString(10, y_axis, "DISBURSEMENTS")
    p.setFont('Helvetica', 12)
    disbursements = Disbursement.objects.filter(matter_id=matter_id)
    total_disbursement_cost = 0

    for disbursement in disbursements:
        y_axis -= 20
        p.drawString(10, y_axis, disbursement.date.strftime("%m/%d/%y"))
        p.drawString(110, y_axis, disbursement.description)
        p.drawString(450, y_axis, str(disbursement.amount))
        p.drawString(510, y_axis, disbursement.tax_choice)
        total_disbursement_cost += disbursement.amount

        # TODO Determine if TAX_CHOICE is NON-TAXABLE, TAXABLE(GST+PST), GST only, PST only

    # Disbursement total
    y_axis -= 20
    p.drawString(fee_disb_labels_x, y_axis, "Disbursement Total")
    p.drawString(450, y_axis, str(total_disbursement_cost))

    # GST on Disbursements
    y_axis -= 20
    p.drawString(fee_disb_labels_x, y_axis, "GST on Disbursements")
    gst_fee = total_disbursement_cost * Decimal(gst_percentage)
    p.drawString(450, y_axis, str(format(gst_fee, '.2f')))

    # PST on Disbursements
    y_axis -= 20
    p.drawString(fee_disb_labels_x, y_axis, "PST on Disbursements")
    pst_fee = total_disbursement_cost * Decimal(pst_percentage)
    p.drawString(450, y_axis, str(format(pst_fee, '.2f')))

    # Disbursements Total with Taxes
    p.setFont('Helvetica-Bold', 12)
    y_axis -= 20
    p.drawString(fee_disb_labels_x, y_axis, "Fee Total with Taxes")
    total_disbursement = total_disbursement_cost + gst_fee + pst_fee
    p.drawString(450, y_axis, str(format(total_disbursement, '.2f')))
    p.setFont('Helvetica', 12)

    # Final costs

    # Total Service Fees and Disbursements
    total_fee_and_disbursement = total_fee + total_disbursement
    y_axis -= 40
    p.drawString(fee_disb_labels_x, y_axis, "Total Fee and Disbursement")
    p.drawString(450, y_axis, str(format(total_fee_and_disbursement, '.2f')))

    # Amount in Trust
    y_axis -= 20
    p.drawString(fee_disb_labels_x, y_axis, "Trust Balance")
    p.drawString(450, y_axis, str(format(matter.trust, '.2f')))

    # Trust transferred at billing
    trust_transferred_at_billing = total_fee_and_disbursement

    if total_fee_and_disbursement > matter.trust:
        trust_transferred_at_billing = matter.trust

    y_axis -= 20
    p.drawString(fee_disb_labels_x, y_axis, "Trust Transferred at Billing")
    p.drawString(450, y_axis, str(format(trust_transferred_at_billing, '.2f')))

    # Balance due
    y_axis -= 40
    p.drawString(fee_disb_labels_x, y_axis, "Balance Now Due")
    balance_now_due = total_fee_and_disbursement - trust_transferred_at_billing
    p.drawString(450, y_axis, str(format(balance_now_due, '.2f')))

    # Amount in Trust after
    y_axis -= 20
    p.drawString(fee_disb_labels_x, y_axis, "Trust Balance")
    p.drawString(450, y_axis, str(format(matter.trust - trust_transferred_at_billing, '.2f')))

    y_axis -= 20
    p.setFont('Helvetica-Bold', 12)
    p.drawString(450, y_axis, "E. & O.E.")
    p.setFont('Helvetica', 12)

    y_axis -= 20
    p.setFont('Helvetica-Bold', 12)
    p.drawString(10, y_axis, "THIS IS OUR ACCOUNT")
    p.setFont('Helvetica', 12)

    y_axis -= 20
    p.drawString(10, y_axis, "WINRIGHT LAW CORPORATION")

    y_axis -= 20
    p.drawString(10, y_axis, matter.lawyer.name)

    # TODO Add Lawyer signature

    # Close the PDF object cleanly.
    p.showPage()
    
    p.save()
    '''
    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


class MatterListView(ListView):
    model = Matter
    context_object_name = 'matter_list'
    template_name = 'website/matter_list.html'


class MatterCreateView(CreateView):
    model = Matter
    template_name = 'website/matter_create.html'
    fields = ['file_number',
              'invoice_date',
              'invoice_number',
              'summary',
              'fee_choice',
              'trust',
              'client',
              'lawyer',
              'notes']

    # TODO use crispy forms

    def get_success_url(self):
        return reverse('matter-list')


class MatterUpdateView(UpdateView):
    model = Matter
    template_name = 'website/matter_create.html'

    def get_success_url(self):
        return reverse('matter-list')


class MatterDetailView(DetailView):
    model = Matter
    template_name = 'website/matter_detail.html'
    context_object_name = 'matter'

    def get_context_data(self, **kwargs):
        context = super(MatterDetailView, self).get_context_data(**kwargs)
        services = Service.objects.filter(matter=self.object.id)
        discounts = Discount.objects.filter(matter=self.object.id)
        disbursements = Disbursement.objects.filter(matter=self.object.id)

        context['services'] = services
        context['discounts'] = discounts
        context['disbursements'] = disbursements
        context['services_cost'] = services.aggregate(total_cost=Sum('amount'))
        context['disbursements_cost'] = disbursements.aggregate(total_cost=Sum('amount'))

        # TODO Add query for services and disbursements linked to this matter

        return context


class MatterDeleteView(DeleteView):
    pass


# For the Service, Discount, and Disbursement. Should make a seamless way to add from the matter detail. Pop up?

class ServiceCreateView(CreateView):
    model = Service
    template_name = 'website/service_create.html'
    fields = ['date', 'description', 'hours', 'amount', 'lawyer', 'notes']

    def form_valid(self, form):
        obj = form.save(commit=False)
        matter = Matter.objects.get(id=self.kwargs['matter_id'])
        obj.matter = matter
        obj.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('matter-detail', kwargs={'pk': self.kwargs['matter_id']})


class DiscountCreateView(CreateView):
    model = Discount
    template_name = 'website/discount_create.html'
    fields = ['name', 'amount', 'discount_choice', 'notes']

    def form_valid(self, form):
        obj = form.save(commit=False)
        matter = Matter.objects.get(id=self.kwargs['matter_id'])
        obj.matter = matter
        obj.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('matter-detail', kwargs={'pk': self.kwargs['matter_id']})


class DisbursementCreateView(CreateView):
    model = Disbursement
    template_name = 'website/disbursement_create.html'
    fields = ['date', 'description', 'amount', 'tax_choice', 'notes']

    def form_valid(self, form):
        obj = form.save(commit=False)
        matter = Matter.objects.get(id=self.kwargs['matter_id'])
        obj.matter = matter
        obj.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('matter-detail', kwargs={'pk': self.kwargs['matter_id']})
