from django.forms import ValidationError
from django.shortcuts import render, redirect
from rest_framework import generics, permissions
from .models import User
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import random
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import login as auth_login  # 이름 충돌을 피하기 위해 alias 사용
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password

from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.serializers import serialize
from django.http import HttpResponse

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token

from .models import Todo
from .serializers import TodoSerializer
from .permissions import IsOwnerOrReadOnly

@csrf_exempt
def get_csrf_token(request):
    if request.method == 'GET':
        csrf_token = get_token(request)
        return JsonResponse({'csrfToken': csrf_token})
    else:
        return JsonResponse({'error': 'GET 요청만 지원됩니다.'})


@csrf_protect
@api_view(['POST'])
def login_api(request):
    if request.method == 'POST':
        id = request.data.get('id')
        password = request.data.get('password')

        if id is None or password is None:
            return JsonResponse({'success': False, 'message': '아이디와 비밀번호를 모두 입력해주세요.'})

        try:
            user = User.objects.get(user_id=id)
            print(f'사용자 아이디: {id}, 사용자 패스워드: {user.user_password}')

        except User.DoesNotExist:
            print('존재하지 않는 아이디입니다.')
            return JsonResponse({'success': False, 'message': '존재하지 않는 아이디입니다.'})

        if not check_password(password, user.user_password):
            print('비밀번호가 올바르지 않습니다.')
            return JsonResponse({'success': False, 'message': '비밀번호가 올바르지 않습니다.'})

        print('로그인 성공')
        return JsonResponse({'success': True, 'message': '로그인 성공'})

    return JsonResponse({'success': False, 'message': 'POST 요청만 지원됩니다.'})



@api_view(['POST'])
@csrf_exempt
def signup_api(request):
    if request.method == 'POST':
        id = request.data.get('id')
        password = request.data.get('password')
        name = request.data.get('name')
        
        # 아이디 중복 확인
        try:
            user = User.objects.get(user_id=id)
            return JsonResponse({'success': False, 'message': '이미 존재하는 아이디입니다.'})
        except User.DoesNotExist:
            pass  # 아이디가 존재하지 않으면 계속 진행
        
        # 비밀번호 검증
        try:
            validate_password(password)
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)})
        
        # 비밀번호 DB 저장 전 해싱
        hashed_password = make_password(password)
        # 사용자 생성 및 랜덤 색상 할당
        new_user = User(user_id=id, user_password=hashed_password, user_name=name)
        new_user.user_color = generate_random_color()
        new_user.save()
        
        return JsonResponse({'success': True, 'message': '회원가입 성공'})
    
    return JsonResponse({'success': False, 'message': 'POST 요청만 지원됩니다.'})

def generate_random_color():
    existing_colors = User.objects.values_list('user_color', flat=True)
    while True:
        # 랜덤한 색상을 #RRGGBB 형식으로 생성
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))

        # 생성한 색상이 이미 존재하는지 확인
        if color not in existing_colors:
            return color
        
        
        
# todos/views.py
class TodoListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Todo.objects.filter(deleted=False)

    serializer_class = TodoSerializer

class TodoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Todo.objects.filter(deleted=False)
    serializer_class = TodoSerializer



    # views.py

@api_view(['POST'])
def create_todo(request):
    serializer = TodoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

