from django.urls import path
from .views import RegisterView, LoginView, UserView, LogoutView, ContractView, CheckAdminView, UserRegistrationView, VoterRegistrationView

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('user', UserView.as_view( )),
    path('logout', LogoutView.as_view()),
    path('contract_address', ContractView.as_view()),
    path('check-admin/<str:metamask_address>/', CheckAdminView.as_view()),
    path('register_user', UserRegistrationView.as_view()),
    path('voter_reg', VoterRegistrationView.as_view())
]   