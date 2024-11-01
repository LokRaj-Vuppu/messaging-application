from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404, HttpResponse
from chat.models import ChatGroup, GroupMessage
from chat.forms import ChatMessageCreationForm, NewgroupForm, ChatRoomEditForm



def home(request):
    try:
        return render(request,'chat/chat_home.html')
    except Exception as error:
        print(f"Exception in home view: {error}")


@login_required
def chat_view(request, chatroom_name='public-chat'):
    print('inside chat_view', chatroom_name , request.user)
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    chat_messages = chat_group.chat_messages.all()[:30]
    form = ChatMessageCreationForm()

    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            print('insde 404 raise')
            return HttpResponse('Not allowed in the group')
            raise Http404()
        for member in chat_group.members.all():
            if member != request.user:
                other_user = member
                break


    if chat_group.groupchat_name:
        if request.user not in chat_group.members.all():
            if request.user.emailaddress_set.filter(verified=True).exists():    
                chat_group.members.add(request.user)
            else:
                messages.warning(request, 'You need to verify your email to join the chat!')
                return redirect('profile-settings')

    if request.htmx:
        form = ChatMessageCreationForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()
            context ={
                'message': message,
                'user': request.user
            }
            return render(request, 'chat/partials/chat_message_p.html', context)
    
    context = {
        'chat_messages': chat_messages, 
        'form': form,
        'other_user': other_user,
        'chatroom_name': chatroom_name,
        'chat_group': chat_group
    }
    return render(request, 'chat/chat.html', context)



@login_required
def get_or_create_chatroom(request, username):
    if request.user.username == username:
        return redirect('home')
    
    other_user = get_object_or_404(User, username=username)
    my_chatrooms = request.user.chat_groups.filter(is_private=True) #fetch available matching chat groups

    chatroom = None

    for chatroom in my_chatrooms:
        if other_user in chatroom.members.all():
            break
    else:
        with transaction.atomic():
            chatroom = ChatGroup.objects.create(is_private=True)
            chatroom.members.add(other_user, request.user)

    return redirect('chatroom', chatroom.group_name)



@login_required
def create_groupchat(request):
    form = NewgroupForm()

    if request.method == 'POST':
        form = NewgroupForm(request.POST)
        if form.is_valid():
            new_groupchat = form.save(commit=False)
            new_groupchat.admin = request.user
            new_groupchat.save()
            new_groupchat.members.add(request.user)
            return redirect('chatroom', new_groupchat.group_name)

    context = {
        'form': form
    }
    return render(request, 'chat/create_groupchat.html', context)



@login_required
def chatroom_edit_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()
    
    form = ChatRoomEditForm(instance=chat_group) 

    if request.method == 'POST':
        form = ChatRoomEditForm(request.POST, instance=chat_group)
        if form.is_valid():
            form.save()
            
            remove_members = request.POST.getlist('remove_members')
            for member_id in remove_members:
                member = User.objects.get(id=member_id)
                chat_group.members.remove(member)  
                
            return redirect('chatroom', chatroom_name) 
    
    context = {
        'form' : form,
        'chat_group' : chat_group
    }   
    return render(request, 'chat/chatroom_edit.html', context) 



@login_required
def chatroom_delete_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()
    
    if request.method == "POST":
        chat_group.delete()
        messages.success(request, 'Chatroom deleted')
        return redirect('home')
    
    return render(request, 'chat/chatroom_delete.html', {'chat_group':chat_group})


@login_required
def chatroom_leave_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user not in chat_group.members.all():
        raise Http404()
    
    if request.method == "POST":
        chat_group.members.remove(request.user)
        messages.success(request, 'You left the Chat')
        return redirect('home')
    
    
def chat_file_upload(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    
    if request.htmx and request.FILES:
        file = request.FILES['file']
        message = GroupMessage.objects.create(
            file = file,
            author = request.user, 
            group = chat_group,
        )
        channel_layer = get_channel_layer()
        event = {
            'type': 'message_handler',
            'message_id': message.id,
        }
        async_to_sync(channel_layer.group_send)(
            chatroom_name, event
        )
    return HttpResponse()