from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home-view'),
    path('matters/', views.MatterListView.as_view(), name='matter-list'),
    path('matters/new/', views.MatterCreateView.as_view(), name='matter-new'),
    path('matters/edit/<int:pk>/', views.MatterUpdateView.as_view(), name='matter-edit'),
    path('matters/<int:pk>/', views.MatterDetailView.as_view(), name='matter-detail'),

    path('services/new/<int:matter_id>/', views.ServiceCreateView.as_view(), name='service-new'),
    path('discounts/new/<int:matter_id>/', views.DiscountCreateView.as_view(), name='discount-new'),
    path('disbursements/new/<int:matter_id>/', views.DisbursementCreateView.as_view(), name='disbursement-new'),

    path('invoice/<int:matter_id>/', views.generate_invoice, name='generate-invoice'),
]