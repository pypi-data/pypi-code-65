
class Node:
    def __init__(self,data_value):
        self.data = data_value
        self.left_child = None
        self.right_child = None
    

class BinarySearchTree:
    def __init__(self):
        self.__root__ = None

    def __insert__(self,current_node, data_value):
        if current_node is None:
            return Node(data_value)
        if data_value < current_node.data:
            current_node.left_child = self.__insert__(current_node.left_child,data_value)
        if data_value > current_node.data:
            current_node.right_child = self.__insert__(current_node.right_child,data_value)
        return current_node

    def insert(self, data_value):
        self.__root__ = self.__insert__(self.__root__, data_value)
    
    def __search__(self,current_node,data_value):
        if current_node is None:
            return False
        if current_node.data is data_value:
            return True
        if data_value > current_node.data:
            return self.__search__(current_node.right_child,data_value)
        if data_value < current_node.data:
            return self.__search__(current_node.left_child,data_value)
    
    def search(self,data_value):
       return self.__search__(self.__root__,data_value)


    def __inorder__(self,current_node):
        if current_node is None:
            return None
        self.__inorder__(current_node.left_child)
        print(current_node.data)
        self.__inorder__(current_node.right_child)

    def inorder(self):
        self.__inorder__(self.__root__)
