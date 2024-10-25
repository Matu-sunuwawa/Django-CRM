import random
from django.core.mail import send_mail
from django.views import generic
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from leads.models import Agent
from .forms import AgentModelForm
from .mixins import OrganizerAndLoginRequiredMixin

# for apply usertype replace "LoginRequiredMixin" by "OrganizerAndLoginRequiredMixin"...it helps to identify "agent" from "organizer"
class AgentListView(OrganizerAndLoginRequiredMixin, generic.ListView):
    template_name = "agents/agent_list.html"

    def get_queryset(self):
        # DO NOT ALLOW USERS DELETE "OTHER AGENTS" WHO BELONGS TO OTHER USER
        # return Agent.objects.all()
        organization = self.request.user.userprofile
        return Agent.objects.filter(organization=organization)

# This one is responsible to "company"(user who has super permission.) not for "agent"
class AgentCreateView(OrganizerAndLoginRequiredMixin, generic.CreateView):
    template_name = "agents/agent_create.html"
    form_class = AgentModelForm

    def get_success_url(self):
        return reverse("agents:agent-list")
    
    # function that responsible for handling "incoming forms" from frontend(html)
    # def form_valid(self, form):
    #     # it is overriding b4 passing the form
    #     # do not commit to database...cuz we want to pass "organization" value w/c presented under Agent model.
    #     agent = form.save(commit=False)
    #     agent.organization = self.request.user.userprofile
    #     # after passing value to "organization"...now we can save.
    #     agent.save()
    #     # it passes the original form
    #     return super(AgentCreateView, self).form_valid(form)

    # INVITE AGENT
    def form_valid(self, form):
            # it is overriding b4 passing the form
            # do not commit to database...cuz we want to pass "organization" value w/c presented under Agent model.
            # agent = form.save(commit=False)
            # agent.organization = self.request.user.userprofile
            # # after passing value to "organization"...now we can save.
            # agent.save()

            user = form.save(commit=False)            
            user.is_agent = True
            user.is_organizer = False
            user.set_password(f"{random.randint(0, 1000000)}")
            user.save()
            Agent.objects.create(
                user=user,
                organization=self.request.user.userprofile,
            )
            send_mail(
                subject="You are invited to be an agent",
                message="You were added as an agent on DJCRM. Please come login to start working.",
                from_email="admin@test.com",
                recipient_list=[user.email]
            )
            # it passes the original form
            return super(AgentCreateView, self).form_valid(form)
    
class AgentDetailView(OrganizerAndLoginRequiredMixin, generic.DetailView):
    template_name = "agents/agent_detail.html"
    context_object_name = "agent"

    def get_queryset(self):
        # return Agent.objects.all()
        organization = self.request.user.userprofile
        return Agent.objects.filter(organization=organization)


class AgentUpdateView(OrganizerAndLoginRequiredMixin, generic.UpdateView):
    template_name = "agents/agent_update.html"
    form_class = AgentModelForm

    def get_success_url(self):
        return reverse("agents:agent-list")
    
    def get_queryset(self):
        # return Agent.objects.all()
        organization = self.request.user.userprofile
        return Agent.objects.filter(organization=organization)


class AgentDeleteView(OrganizerAndLoginRequiredMixin, generic.DeleteView):
    template_name = "agents/agent_delete.html"
    context_object_name = "agent"

    def get_success_url(self):
        return reverse("agents:agent-list")

    def get_queryset(self):
        # return Agent.objects.all()
        organization = self.request.user.userprofile
        return Agent.objects.filter(organization=organization)