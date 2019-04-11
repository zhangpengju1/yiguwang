from haystack import indexes
from database.models import Specification


class SpecificationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True,use_template=True)

    def get_model(self):
        return Specification

    def index_queryset(self, using=None):
        return self.get_model().objects.all()