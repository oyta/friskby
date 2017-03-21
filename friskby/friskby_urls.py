from django.conf.urls import url, include

from views import Home
from views import Adm
from views import JSHome
from views import Quick
from views import Median
from views import Map

urlpatterns = [
    url(r'^friskby/adm/$' , Adm.as_view(), name = "friskby.view.adm"),
    url(r'friskby/$'      , Home.as_view()),
    url(r'legacy/$'       , JSHome.as_view()),
    url(r'^$'             , Quick.as_view(), name = "friskby.view.quick"),
    url(r'median/$'       , Median.as_view(), name = "friskby.view.median"),

    url(r'map/$'       , Map.as_view(), name = "friskby.view.map")
]
