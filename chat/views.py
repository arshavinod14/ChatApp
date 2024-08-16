from django.shortcuts import render, get_object_or_404, redirect
from .models import ChatGroup, GroupMessage
from django.contrib.auth.decorators import login_required
from django.http import Http404
from asgiref.sync import async_to_sync
from django.http import HttpResponse
from .forms import *
from django.contrib.auth import get_user_model
from django.contrib import messages
from channels.layers import get_channel_layer



@login_required
def chatHomepage(request, chatroom_name='public-chat'):
    profile = request.user.profile
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    
    chat_messages = chat_group.chat_messages.all()[:30]
    form = ChatmessageCreateForm()

    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            chat_group.members.add(request.user)  # Allow rejoining for private groups
        for member in chat_group.members.all():
            if member != request.user:
                other_user = member
                break

    if not chat_group.is_private:
        if request.user not in chat_group.members.all():
            chat_group.members.add(request.user)

    # Ensure all chat groups have a unique groupchat_name
    for group in request.user.chat_groups.all():
        if not group.groupchat_name:
            group.groupchat_name = group.group_name
            group.save()

    # Sort chat groups by last_activity (newest first)
    chat_groups = request.user.chat_groups.all().order_by('-last_activity')

    if request.htmx:
        form = ChatmessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()
            
            # Update last_activity field for the chat group only when a message is sent
            chat_group.update_last_activity()

            context = {
                'chat_messages': chat_messages,
                'user': request.user
            }
            return render(request, 'partials/chat_message_p.html', context)
        
    context = {
        'chat_messages': chat_messages,
        'form': form,
        'other_user': other_user,
        'chatroom_name': chatroom_name,
        'chat_group': chat_group,
        'profile': profile,
        'chat_groups': chat_groups,  # Pass sorted chat groups to the template
    }
    return render(request, 'chatHomepage.html', context)





@login_required
def get_or_create_chatroom(request, name):
    profile = request.user.profile
    if request.user.name == name:
        return redirect('home')
    
    User = get_user_model()
    other_user = User.objects.get(name=name)
    my_chatrooms = request.user.chat_groups.filter(is_private=True)
    
    chatroom = None
    if my_chatrooms.exists():
        for room in my_chatrooms:
            if other_user in room.members.all():
                chatroom = room
                break
    
    if not chatroom:
        chatroom = ChatGroup.objects.create(is_private=True)
        chatroom.members.add(other_user, request.user)
    else:
        chatroom.members.add(request.user)  # Allow rejoining by adding the user back to the group

    return redirect('chatroom', chatroom_name=chatroom.group_name)



@login_required
def create_groupchat(request):
    profile = request.user.profile
    form  = NewGroupForm()
    if request.method == 'POST':
        form = NewGroupForm(request.POST,request.FILES)
        if form.is_valid():
            new_groupchat = form.save(commit=False)
            new_groupchat.admin = request.user
            new_groupchat.save()
            new_groupchat.members.add(request.user)
            return redirect('chatroom',new_groupchat.group_name)
    context = {
        'form': form,
        'profile': profile

    }
    return render(request,'create_groupchat.html',context)


from django.contrib.auth import get_user_model

@login_required
def chatroom_edit_view(request, chatroom_name):
    profile = request.user.profile
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()

    form = ChatRoomEditForm(instance=chat_group)
    if request.method == 'POST':
        form = ChatRoomEditForm(request.POST, request.FILES, instance=chat_group)
        if form.is_valid():
            form.save()

            remove_members = request.POST.getlist('remove_members')
            User = get_user_model()
            for member_id in remove_members:
                try:
                    member = User.objects.get(id=member_id)
                    chat_group.members.remove(member)
                    if chat_group.group_name == 'public-chat':
                        member.profile.removed_from_public = True
                        member.profile.save()
                except User.DoesNotExist:
                    print(f"User with ID {member_id} does not exist.")

            return redirect('chatroom', chatroom_name)
        else:
            print(form.errors)  # Print form errors if the form is not valid

    # Fetch all members of the chat group
    members = chat_group.members.all().select_related('profile')

    context = {
        'form': form,
        'chat_group': chat_group,
        'members': members,
        'profile': profile
    }
    return render(request, 'chatroom_edit.html', context)




@login_required
def chatroom_delete_view(request,chatroom_name):
    profile = request.user.profile
    chat_group = get_object_or_404(ChatGroup,group_name=chatroom_name)
    print("chatgroup:",chat_group)
    if request.user != chat_group.admin:
        raise Http404()
    
    if request.method == 'POST':
        chat_group.delete()
        messages.success(request,'Chatroom deleted successfully')
        return redirect('chatHomepage')
    context = {
        'profile':profile,
        'chat_group':chat_group,
    }
    return render(request,'chatroom_delete.html',context)

@login_required
def chatroom_leave_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user not in chat_group.members.all():
        raise Http404()
    
    if request.method == 'POST':
        chat_group.members.remove(request.user)
        messages.success(request, 'You left the chat')
        return redirect('chatHomepage')
    
    return render(request, 'chat_exit.html', {'chat_group': chat_group})


def chat_file_upload(request,chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)

    if request.htmx and request.FILES:
        file = request.FILES['file']
        message = GroupMessage.objects.create(
            file = file,
            author = request.user,
            group = chat_group,
        )

        channel_layer  =  get_channel_layer()
        event = {
            'type': 'message_handler',
            'message_id':message.id
        }

        async_to_sync(channel_layer.group_send)(
            chatroom_name,event
        )
    return HttpResponse
