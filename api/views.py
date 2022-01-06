from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .olshop import search

@api_view(['GET'])
def search_product(request, keyword) -> list:
	if request.method == 'GET':
		try:
			result = search(keyword)
		except Exception as e:
			print(e)
			return Response({"detail":str(e)},status=status.HTTP_400_BAD_REQUEST)

		return Response(result)
