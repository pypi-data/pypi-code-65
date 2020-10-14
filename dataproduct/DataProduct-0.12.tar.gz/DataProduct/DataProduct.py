from conection.dbconection import getConnection
from entity.DTProduct import DTProduct

def getProducts():   
   try:
        # Get the sql connection
     queryproduct='Select * from Producto'
     connection = getConnection()
     cursor = connection.cursor()

        # Execute the sql query
     cursorp =cursor.execute(queryproduct)
     listproduct=[]
     for p in cursorp:
            id=int(p[0])
            image=str(p[1])
            perobjet=DTProduct(id,image)
            listproduct.append(perobjet)
     return listproduct
     
   except Exception as e:
    print("Error listing products: ", e) 
   finally:
    connection.close()        
def getProduct(idprod):   
   try:
        # Get the sql connection
     queryproduct='Select * from Producto where IdProducto=?'
     connection = getConnection()
     cursor = connection.cursor()

        # Execute the sql query
     cursorp =cursor.execute(queryproduct,[idprod])
     result=cursor.fetchall();
     row=result[0]
     id=int(row[0])
     image=str(row[1])
     perobjet=DTProduct(id,image)
     return perobjet
     
   except Exception as e:
    print("Error searching products: ", e) 
   finally:
    connection.close() 
def insertProduct(product):
  try:
           connection = getConnection()
           query = "insert into Producto values (?)" 
           cursor = connection.cursor()

           # Execute the sql query
           cursor.execute(query, [product.image])

           # Commit the data
           connection.commit()
           return ("Data Saved Successfully")

  except Exception as e:
           return ("Something wrong ,please check",e)

  finally:
           # Close the connection
           connection.close()
def updateProduct(product):
  try:
           connection = getConnection()
           query = "Update Producto Set ImgProducto=? where IdProducto=?" 
           cursor = connection.cursor()

           # Execute the sql query
           cursor.execute(query, [product.image,product.id])

           # Commit the data
           connection.commit()
           return ("Data Updated Successfully")

  except Exception as e:
           return ("Something wrong ,please check",e)

  finally:
           # Close the connection
           connection.close() 
def deleteProduct(product):
  try:
           connection = dbconection.getConnection()
           query = "delete from Producto where IdProducto=?" 
           cursor = connection.cursor()

           # Execute the sql query
           cursor.execute(query, [product.id])

           # Commit the data
           connection.commit()
           return ("Data Deleted Successfully")

  except Exception as e:
           return ("Something wrong ,please check",e)

  finally:
           # Close the connection
           connection.close() 

list=getProducts()
for x in list: 
  print("------------")
  print(x.id)
  print("------------")
  print(x.image)
  print("------------")

obj=getProduct(10)
print(obj.id)
print(obj.image)
""" 
def getProduct(id): 
    dprodut=DTProduct(0,"")
    for p in getProducts():
     if(id==p.id):
      dprodut=p;
    return dprodut
prouct=DTProduct(17,"gds.jpg")
 mensaje=insertProduct(prouct)
 mensaje=updateProduct(prouct)
 mensaje=deleteProduct(prouct)

  list=getProducts()
  for x in list: 
 print("------------")
 print(x.id)
 print("------------")
 print(x.image)
 print(mensaje)
 obj=getProduct(5)
 print(obj.id)
 print(obj.image)

"""


"""
    try:


      Get the sql connection
      queryproduct='Select * from Producto where IdProducto=?'
       connection = con.getConnection()
      cursor = connection.cursor()
        # Execute the sql query
       cursor.execute(queryproduct,[id])

       idproducto=result[0]
       imagep=result[1]
      perobjet=DTProduct(idproducto,image)
    
      return perobjet
"""