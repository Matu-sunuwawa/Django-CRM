from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from agents.mixins import OrganizerAndLoginRequiredMixin
from django.http import HttpResponse
from .models import Lead, Agent, Category
# from django.contrib.auth.forms import UserCreationForm
from .forms import (
    LeadForm, 
    LeadModelForm, 
    CustomUserCreationForm, 
    AssignAgentForm, 
    LeadCategoryUpdateForm,
    CategoryModelForm
)

# from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import generic

# CRUD+L create,read,update and delete + list
# ListView, CreateView, DetailView, DeleteView, UpdateView

class SignupView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm

    def get_success_url(self):
        # return "/leads"
        return reverse("login")

class LandingPageView(generic.TemplateView):
    template_name = "landing.html"

def landing_page(request):
    return render(request, "landing.html")

class LeadListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/lead_list.html"
    # queryset = Lead.objects.all()
    context_object_name = "leads"

    # Django only executes the function when the "return" method called..."return queryset"
    # simply queryset is "restricting" the "context_object_name"...rather than allowing to "fetch all data"...made restriction
    def get_queryset(self):
        user = self.request.user
        # queryset = Lead.objects.all()

        # initial queryset of leads for the entire organization
        if user.is_organizer:
            # i know your confusion..."user.userprofile" this meant on models.py there are "organization"(in Agent model) that has access to "UserProfile" model...
            # and the "user"(in UserProfile model) has OneToOne r/ship with "User" model...so we can access like "user.userprofile"..."User.UserProfile"..."user"=="self.request.user"

            # organization should filter only their "leads"
            # queryset = Lead.objects.filter(organization=user.userprofile)
            queryset = Lead.objects.filter(organization=user.userprofile, agent__isnull=False)
        # if self.request.user.is_agent:
        else:
            # "user.agent.organization"...there are "Agent" model and inside model there is "organization"...
            # so,"User.Agent.organization"=="self.request.user.agent.organization"

            # the logged-in agent should filter leads who belong to current "organization"
            # queryset = Lead.objects.filter(organization=user.agent.organization)
            queryset = Lead.objects.filter(organization=user.agent.organization, agent__isnull=False)
            
            # filter for the agent that is logged in
            # 1,we want to fiter for Lead...2,for agent that logged-in...3,and it reference "Agent" model...4,and that has OneToOneField to the "User" model
            # why we say "agent__user" is to access agent through "his/her name" rather than "Email"..."agent" display "email" and is is not good to filter using email
            # AND THAT IS DONE USING ONE LINE OF CODE...HAHAHA
            queryset = queryset.filter(agent__user=self.request.user)
        return queryset
    
    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(LeadListView, self).get_context_data(**kwargs)
        if user.is_organizer:
            queryset = Lead.objects.filter(
                organization=user.userprofile, agent__isnull=True
            )
            context.update({
                "unassigned_leads":queryset
            })
        return context

def lead_list(request):
    # return HttpResponse("Hello World")
    leads = Lead.objects.all()
    context = {
        "leads": leads
    }
    # return render(request, 'leads/home_page.html')
    return render(request, 'leads/lead_list.html', context)

class LeadDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/lead_detail.html"
    # queryset = Lead.objects.all()
    context_object_name = "lead"

    def get_queryset(self):
        user = self.request.user
 
        # initial queryset of leads for the entire organization
        if user.is_organizer:
            queryset = Lead.objects.filter(organization=user.userprofile)
        else:
            queryset = Lead.objects.filter(organization=user.agent.organization)
             # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=self.request.user)
        return queryset

def lead_detail(request, pk):
    print(pk)
    lead = Lead.objects.get(id=pk)
    print(lead)
    context = {
        "lead": lead
    }
    # return HttpResponse("here is the detail view")
    return render(request, "leads/lead_detail.html", context)


# do not allow the "Agent" to create new leads(potentail customers)
class LeadCreateView(OrganizerAndLoginRequiredMixin, generic.CreateView):
    template_name = "leads/lead_create.html"
    form_class = LeadModelForm

    def get_success_url(self):
        # return "/leads"
        return reverse("leads:lead-list")
    def form_valid(self, form):
        # TODO send email
        lead = form.save(commit=False)
        lead.organization = self.request.user.userprofile
        lead.save()
        send_mail(
            subject="A lead has been created",
            message="Go to the site to see the new lead",
            from_email="test@test.com",
            recipient_list=["test2@test.com"]
        )
        return super(LeadCreateView, self).form_valid(form)

def lead_create(request):
    print(request.POST)
    form = LeadModelForm()
    if request.method == "POST":
        print("Recieving a post request")
        form = LeadModelForm(request.POST)
        if form.is_valid():
            # print("Form is valid")
            # # this one is better one of "print(request.POST)"
            # print(form.cleaned_data)

            # first_name = form.cleaned_data['first_name']
            # last_name = form.cleaned_data['last_name']
            # age = form.cleaned_data['age']
            # # agent = Agent.objects.first()
            # agent = form.cleaned_data['agent']

            # Lead.objects.create(
            #     first_name=first_name,
            #     last_name=last_name,
            #     age=age,
            #     agent=agent
            # )
            # print("The lead has been created")

            form.save()
            return redirect('/leads')
    context = {
        # "form": LeadForm()
        "form": form
    }
    return render(request, "leads/lead_create.html", context)


class LeadUpdateView(OrganizerAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_update.html"
    # queryset = Lead.objects.all()
    form_class = LeadModelForm

    # cuz the agent can not make "update" filter only "organization"
    def get_queryset(self):
        user = self.request.user
 
        # initial queryset of leads for the entire organization
        return Lead.objects.filter(organization=user.userprofile)

    def get_success_url(self):
        # return "/leads"
        return reverse("leads:lead-list")

# using model form
def lead_update(request, pk):
    lead = Lead.objects.get(id=pk)
    # instance is the single instance of the model that we want to update
    form = LeadModelForm(instance=lead)
    if request.method == "POST":
        print("Recieving a post request")
        form = LeadModelForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            return redirect("/leads")
    context = {
        "form": form,
        "lead": lead
    }
    return render(request, 'leads/lead_update.html', context)


class LeadDeleteView(OrganizerAndLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/lead_delete.html"
    # queryset = Lead.objects.all()

    def get_success_url(self):
        # return "/leads"
        return reverse("leads:lead-list")


    # cuz the agent can not make "delete", filter only "organization"
    def get_queryset(self):
        user = self.request.user
 
        # initial queryset of leads for the entire organization
        return Lead.objects.filter(organization=user.userprofile)


def lead_delete(request, pk):
    lead = Lead.objects.get(id=pk)
    lead.delete()
    return redirect("/leads")

# using normal form
# def lead_update(request, pk):
    lead = Lead.objects.get(id=pk)
    form = LeadForm(request.POST)
    if request.method == "POST":
        print("Recieving a post request")
        form = LeadForm(request.POST)
        if form.is_valid():
            print("Form is valid")
            # this one is better one of "print(request.POST)"
            print(form.cleaned_data)

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            age = form.cleaned_data['age']
            # agent = Agent.objects.first()
            # agent = form.cleaned_data['agent']

            lead.first_name = first_name
            lead.last_name = last_name
            lead.age = age
            lead.save()
            print("The lead has been updated")
            return redirect('/leads')
    context = {
        "form": form,
        "lead": lead
    }
    return render(request, 'leads/lead_update.html', context)


class AssignAgentView(OrganizerAndLoginRequiredMixin, generic.FormView):
    template_name = "leads/assign_agent.html"
    form_class = AssignAgentForm

    # def get_form_kwargs(self):
    #     return {
    #         "request": self.request
    #     }

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            "request": self.request
        })
        return kwargs

    def get_success_url(slef):
        return reverse("leads:lead-list")

    def form_valid(self, form):
        print(form.cleaned_data["agent"])
        agent = form.cleaned_data["agent"] # it returns the "email"
        lead = Lead.objects.get(id=self.kwargs["pk"])
        lead.agent = agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)



class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/category_list.html"
    context_object_name = "category_list"


    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user
        if user.is_organizer:
            # filter the "leads" w/c belongs to logged-in "organization"
            queryset = Lead.objects.filter(organization=user.userprofile)
        else:
            # filter the "leads" w/c belongs to logged-in "agent"...and filter the logged-in "agent" w/c belongs to specific "organization"
            queryset = Lead.objects.filter(organization=user.agent.organization)
        context.update({
            "unassigned_lead_count": queryset.filter(category__isnull=True).count()
        })
        return context

    def get_queryset(self):
        user = self.request.user

        # initial queryset of leads for the entire organization
        if user.is_organizer:
            queryset = Category.objects.filter(organization=user.userprofile)
        else:
            queryset = Category.objects.filter(organization=user.agent.organization)
        return queryset
    

class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/category_detail.html"
    context_object_name = "category"

    # even if i comment this out it works...if i passed category.leads.allin "details" template "{% for lead in category.leads.all %}"
    # def get_context_data(self, **kwargs):
    #     context = super(CategoryDetailView, self).get_context_data(**kwargs)

    '''
    we can express it in different way...using "self"...
    the way we can fetch all the "leads" that belong to specific category is using "self.get_object()" syntax...w/c is part os "DetailView" and "UpdateView" cuz it is dealing about "specific object"
    there are d/t methods around 3...
    1,usign "get_object()" that belong to DetailView and make "filter"...
    2,using "self.get_object().lead_set.all()"..."self.get_object()" fetches the actual category and "lead_set" that fetches all the leads that assigned to the category...
    - reminder!!! where is the name "lead_set" comes from?...it is simply take the model "Lead" and adjust to lowercase..."lead" and add "underscore + set"...
    - but second reminder!!! it works based on "Foreign key usage"...example, in this senario we declare ForeignKey to the "category" model...OK, what will be the syntax for reversed case?...==>"self.get_object().category_set.all()"...
    - more updated version of "lead_set" is by putting "related_name="leads"" inside declared ForeignKey...it will be ==>"self.get_object().leads.all()"
    3, this one is really have fun...by using "related_name="leads""...we can use "context_obeject_name" + "leads.all()"=="category.leads.all()"..."ACTUALLY THAT IS POSSIBLE"
    '''

    #     # qs = Lead.objects.filter(category=self.get_object())
    #     # it wil fetch all "leads" that assigned to "category"
    #     # self.get_object().lead_set.all()
    #     leads = self.get_object().leads.all()

    #     context.update({
    #         "leads": leads
    #     })
    #     return context

    def get_queryset(self):
        user = self.request.user

        # initial queryset of leads for the entire organization
        if user.is_organizer:
            queryset = Category.objects.filter(organization=user.userprofile)
        else:
            queryset = Category.objects.filter(organization=user.agent.organization)
        return queryset
    
class CategoryCreateView(OrganizerAndLoginRequiredMixin, generic.CreateView):
    template_name = "leads/category_create.html"
    form_class = CategoryModelForm

    def get_success_url(self):
        # return "/leads"
        return reverse("leads:category-list")
    
    def form_valid(self, form):
        # TODO send email
        category = form.save(commit=False)
        category.organization = self.request.user.userprofile
        category.save()
        return super(CategoryCreateView, self).form_valid(form)
    
class CategoryUpdateView(OrganizerAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/category_update.html"
    form_class = CategoryModelForm

    def get_success_url(self):
        # return "/leads"
        return reverse("leads:category-list")

    def get_queryset(self):
        user = self.request.user

        # initial queryset of leads for the entire organization
        if user.is_organizer:
            queryset = Category.objects.filter(organization=user.userprofile)
        else:
            queryset = Category.objects.filter(organization=user.agent.organization)
        return queryset
    
class CategoryDeleteView(OrganizerAndLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/category_delete.html"

    def get_success_url(self):
        # return "/leads"
        return reverse("leads:category-list")

    def get_queryset(self):
        user = self.request.user

        # initial queryset of leads for the entire organization
        if user.is_organizer:
            queryset = Category.objects.filter(organization=user.userprofile)
        else:
            queryset = Category.objects.filter(organization=user.agent.organization)
        return queryset
    
    

class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_category_update.html"
    form_class = LeadCategoryUpdateForm
    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(organization=user.userprofile)
        else:
            queryset = Lead.objects.filter(organization=user.agent.organization)
            queryset = queryset.filter(agent__user=self.request.user)
        return queryset

    def get_success_url(self):
        # return reverse("leads:lead-list")
        # self.get_object()...that will return the actually "leads"(the lead we are dealing with)..."self.get_object().id" this one will grab the "primary key" of the object
        return reverse("leads:lead-detail", kwargs={"pk":self.get_object().id})
