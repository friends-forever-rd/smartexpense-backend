from django.urls import path
from apps.expense.views import PullView, PushView

urlpatterns = [
    path("pull", PullView.as_view(), name="expense-pull"),
    path("push", PushView.as_view(), name="expense-push"),
]
