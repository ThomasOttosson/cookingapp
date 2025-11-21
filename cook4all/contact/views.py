from django.shortcuts import render
from django.views.generic import TemplateView


class ContactView(TemplateView):
    template_name = "contact/contact.html"

    def post(self, request, *args, **kwargs):
        # Dummy form submission: just render the same page with a success message
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        context = {
            "success": True,
            "name": name,
            "email": email,
            "message": message,
        }
        return render(request, self.template_name, context)
