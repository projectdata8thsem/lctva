from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from app.views import IndexView, DashboardView, StreamActivateView, StreamDeactivateView, GraphView, FriendsGraphView, ExtraView


urlpatterns = [
    url(r'^$', IndexView.as_view(), name="index_view"),
    url(r'^dashboard/$', login_required(DashboardView.as_view()), name="dashboard_view"),
    url(r'^extra/$', login_required(ExtraView.as_view()), name="extra_view"),
    url(r'^stream_activate/$', login_required(StreamActivateView.as_view()), name="stream_activate"),
    url(r'^stream_deactivate/$', login_required(StreamDeactivateView.as_view()), name="stream_deactivate"),
    url(r'^api/graph/$', GraphView.as_view(), name="graph_view"),
    url(r'^api/graph/friends/$', FriendsGraphView.as_view(), name="friends_graph_view"),
]
