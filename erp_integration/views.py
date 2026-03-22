from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

# @api_view(["POST"])
# def finance_clearance(request):
#     return Response({
#         "status": "approved",
#         "reference": "FIN-2026-001",
#         "comments": ""
#     })


from students.models import Student
from .services import get_finance_clearance


@api_view(["POST"])
def finance_clearance(request):
    student_number = request.data.get("student_number")

    if not student_number:
        return Response({"error": "student_number is required"}, status=400)

    student = Student.objects.filter(student_number=student_number).first()
    if not student:
        return Response({"error": "Student not found"}, status=404)

    data = get_finance_clearance(student)
    return Response(data)