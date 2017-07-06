import telepot
from telepot.delegate import per_chat_id, create_open, pave_event_space, include_callback_query_chat_id
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

import configparser
import random

from server import send_mail

config = configparser.ConfigParser()
config.read('config.ini')

CHAIRPERSON_ID = config['CONGRESS']['chairperson_id']

class Member(telepot.helper.ChatHandler):
    '''
    The chat handler of each member
    '''
    def __init__(self, seed_tuple, polls, members, students, **kwargs):
        super(Member, self).__init__(seed_tuple, **kwargs)
        # linked to Congress
        self._polls = polls
        self._students = students
        self._members = members

        # by chat
        if self.id in self._members:
            self._stu_id = self._members[self.id]['_stu_id']
            self._reg_code = self._members[self.id]['_reg_code']
            self._is_verified = self._members[self.id]['_is_verified']
            self._is_chairperson = self._members[self.id]['_is_chairperson']
            self._ballot_view = self._members[self.id]['_ballot_view']
            self._draft_poll = self._members[self.id]['_draft_poll']
            self._ballot_ident = self._members[self.id]['_ballot_ident']
        else:
            self._stu_id = ''
            self._reg_code = ''
            self._is_verified = False
            self._is_chairperson = False
            self._ballot_view = None
            self._draft_poll = None
            self._ballot_ident = None

    def _register(self, stu_id):
        '''
        For a member to register for starting the chat.
        '''
        if stu_id.upper() not in self._students:
            self.sender.sendMessage('請輸入學生代表學號')
        elif not self._reg_code == '' and not self._is_verified:
            self.sender.sendMessage('驗證碼已寄發，請到 NTU Mail 查看')
        else:
            self._stu_id = stu_id.upper()
            self._is_chairperson = True if stu_id.upper() == CHAIRPERSON_ID.upper() else False
            self._reg_code = ''.join(random.choice('0123456789') for i in range(5))
            send_mail(stu_id=stu_id, reg_code=self._reg_code)
            print('<{stu_id}> <{chat_id}> register {reg_code}'.format(stu_id=self._stu_id, reg_code=self._reg_code, chat_id=self.id))
            self.sender.sendMessage('驗證碼已寄發')

    def _verify(self, reg_code):
        '''
        For a member to verify using the register code send to the NTU mailbox.
        '''
        if self._is_verified:
            self.sender.sendMessage('已完成驗證')
        elif self._reg_code == reg_code:
            self._is_verified = True
            self.sender.sendMessage('成功登入')
        else:
            self.sender.sendMessage('驗證碼錯誤')

    # TODO: check in

    def _default_reply(self):
        if self._is_verified:
            self.sender.sendMessage('請專心開會')
        else:
            self.sender.sendMessage('登入：/login <學號>\n輸入授權碼：/code <驗證碼>')

    def _ask(self, question):
        '''
        For the chairperson to start a poll.
        '''
        self.sender.sendMessage('Create poll: {}'.format(question))
        return Poll(question, self._students)

    def _revoke_ballot(self, msg_ident):
        self.bot.editMessageText(msg_identifier=msg_ident,text='選票註銷', reply_markup=None)

    def _send_ballot(self):
        '''
        Send ballot to all members after command /vote is used
        '''
        text = self._polls[-1].question
        choices = self._polls[-1].choices
        keyboard = InlineKeyboardMarkup(inline_keyboard=[list(map(lambda c: InlineKeyboardButton(text=str(c), callback_data=str(c)), choices))])
        sent = self.sender.sendMessage(text, reply_markup=keyboard)
        self._ballot_ident = telepot.message_identifier(sent)
        self._ballot_view = telepot.helper.Editor(self.bot, sent)

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        if content_type != 'text':
            self._default_reply()
            return

        content = msg['text'].strip().split(' ',1)

        command = content[0]
        param = content[-1]

        if command[0] != '/':
            self._default_reply()
            return

        if self._is_verified:
            if command == '/vote':
                if len(self._polls) == 0 or not self._polls[-1].is_active:
                    self.sender.sendMessage('目前沒有投票')
                else:
                    if self._ballot_view is not None:
                        self._revoke_ballot(self._ballot_ident)
                        self._send_ballot()
                    else:
                        self._send_ballot()
            else:
                if self._is_chairperson:
                    if command == '/ask':
                        if len(self._polls) > 0 and self._polls[-1].is_active:
                            self.sender.sendMessage('投票尚在進行，請先結束投票')
                        else:
                            self._draft_poll = self._ask(param)
                    elif command == '/add':
                        if self._draft_poll is not None:
                            self._draft_poll.add(param)
                            self.sender.sendMessage('Add choice: {}'.format(param))
                        else:
                            self.sender.sendMessage('現階段沒有投票，請使用 /ask 新增問題')
                    elif command == '/go':
                        if self._draft_poll is not None:
                            self._draft_poll.start()
                            self._polls.append(self._draft_poll)
                            self._draft_poll = None
                            self.sender.sendMessage('投票開始')
                        else:
                            self.sender.sendMessage('現階段沒有投票，請使用 /ask 新增問題')
                    elif command == '/end':
                        if len(self._polls) > 0 and self._polls[-1].is_active:
                            self._polls[-1].end()
                        else:
                            self.sender.sendMessage('現階段沒有投票，請使用 /ask 新增問題')
                    else:
                        self.sender.sendMessage('新增問題：/ask <問題>\n新增選項：/add <選項>\n開始投票：/go\n結束投票：/end')
                else:
                    self._default_reply()
        else:
            if command == '/login':
                self._register(stu_id=param)
            elif command == '/code':
                self._verify(reg_code=param)

    def on_callback_query(self, msg):
        '''
        Handle ballot
        '''
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        if telepot.origin_identifier(msg) != self._ballot_ident:
            self._revoke_ballot(telepot.origin_identifier(msg))
        else:
            msg = self._polls[-1].vote(self._stu_id, query_data)
            self._ballot_view.editMessageText(text='{question}\n選擇：{choice}'.format(question=self._polls[-1].question, choice=query_data),reply_markup=None)
            self._ballot_view = None
            self._ballot_ident = None

    def on__idle(self, event):
        self.close()

    def on_close(self, ex):
        self._members[self.id] = {
            '_stu_id': self._stu_id,
            '_reg_code': self._reg_code,
            '_is_verified': self._is_verified,
            '_is_chairperson': self._is_chairperson,
            '_draft_poll': self._draft_poll,
            '_ballot_view': self._ballot_view,
            '_ballot_ident': self._ballot_ident
        }

    def __str__(self):
        return self._stu_id

class Poll(object):
    def __init__(self, question, students):
        self.id = ''.join(random.choice('0123456789ABCDEF') for i in range(8))
        self.question = question
        self.choices = list()
        self.is_active = False
        self.result = dict()
        self.ballots = dict() # stu_id: Ballot

        self.students = students

    def add(self, choice):
        self.choices.append(choice)

    def vote(self, stu_id, choice):
        if self.ballots[stu_id].is_valid:
            self.ballots[stu_id].stamp(choice)
            return '選擇：{choice}'.format(choice=choice)
        else:
            return '投票已結束'

    def start(self):
        # If adding choices is skipped
        if len(self.choices) == 0:
            self.choices = ['贊成', '反對']

        # Initialize counts of choices
        self.result['棄權'] = 0
        for choice in self.choices:
            self.result[choice] = 0

        # Initialize ballot box
        for stu_id in self.students:
            self.ballots[stu_id] = Ballot(stu_id, self.id)

        self.is_active = True
        return self

    def end(self):
        # Open ballot
        print('<{id}> {question} ============'.format(id=self.id, question=self.question))
        for stu_id, ballot in self.ballots.items():
            self.result[ballot.choice] += 1
            self.is_active = False
            print('<{stu_id}> vote {choice}'.format(stu_id=stu_id, choice=ballot.choice))
        print('<{id}> {question}: {result}'.format(id=self.id, question=self.question, result=self.result))

        # Save result
        with open('data/{id}-{question}.txt'.format(id=self.id, question=self.question), 'w') as f:
            f.write('<{id}> {question}'.format(id=self.id, question=self.question))
            for choice, count in self.result:
                f.write('{choice}: {num}'.format(choice=choice, num=count))
            for stu_id, ballot in self.ballots.items():
                self.result[ballot.choice] += 1
                self.is_active = False
                f.write('<{stu_id}> vote {choice}'.format(stu_id=stu_id, choice=ballot.choice))
        return self


    def __str__(self):
        return self.question

class Ballot(object):
    def __init__(self, stu_id, poll_id):
        self.poll_id = poll_id
        self.stu_id = stu_id
        self.choice = '棄權'
        self.is_used = False
        self.is_valid = True

    def stamp(self, choice):
        if self.is_valid:
            self.choice = choice
            self.is_used = True
            return self
        else:
            return self

    def __str__(self):
        return '{stu_id} chooses {choice} to {poll_id}'.format(stu_id=self.stu_id, choice=self.choice, poll_id=self.poll_id)

class Congress(telepot.DelegatorBot):
    def __init__(self, token, members, polls, students):
        self._polls = polls
        self._members = members
        self._students = students

        super(Congress, self).__init__(token, [
            include_callback_query_chat_id(pave_event_space())(
                per_chat_id(types=['private']),
                create_open,
                Member,
                self._polls,
                self._members,
                self._students,
                timeout=20
            ),
        ])
