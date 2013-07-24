from django.utils.translation import ugettext as _
import django.db.models as m
import refs

from utils.models import QuerySetModel, RequestQuerySet, QuerySetManager
from . import exceptions

"""
Heads up!

This app only supports Postgresql
"""

class NodeManager(m.Manager):
    def ancestors(self, node):
        """
        Perform a Postgresql only RECURSIVE SELECT, fetching an entire
        transitive closure of nodes by parent.
        """
        SQL = """
            WITH RECURSIVE node(id, ref_id, parent_id) AS (
                  SELECT id, ref_id, parent_id FROM dag_node WHERE id = %s
                  UNION
                    SELECT tt.id, tt.ref_id, tt.parent_id
                    FROM dag_node as tt, node
                    WHERE node.parent_id = tt.id)
                SELECT * FROM node ORDER BY id;
            """
        return self.raw(SQL, [node.pk])


class Graph(m.Model):
    def insert(self, obj, parent=None, child=None):
        if child and parent != child.parent:
            raise InsertError(_("{parent} is not parent of {child}").format(parent=parent, child=child))
        node = self.nodes.create(parent=parent)
        if child:
            child.parent = node
        return node

    def remove(self, obj):
        node = self.nodes.get(obj=obj)
        for child in node.children():
            child.parent = node.parent
        node.delete()


class Node(m.Model):
    graph = m.ForeignKey(Graph, related_name='nodes')
    parent = m.ForeignKey('self', related_name='children')
    obj = refs.OneToOneRef()

    class Meta:
        unique_together = [('obj', 'graph')]

    def family(self):
        return self.graph.nodes.all()

    def children(self):
        return self.graph.nodes.filter(parent=self)

    def ancestors(self):
        return list(self.__class__.objects.ancestors(self))

    def descendants(self):
        return set(self.family()) - set(self.ancestors()) - set(self)


    def is_family_of(self, node):
        return self.graph == other.graph

    def is_descendant_of(self, node):
        return node in self.ancestors()

    def is_ancestor_of(self, node):
        return self.is_descendant_of(node)
