# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class BankCase(models.Model):
    id = models.BigAutoField(primary_key=True)
    cas_se_no = models.BigIntegerField()
    project_name = models.CharField(max_length=255)
    cas_state = models.IntegerField()
    cas_m = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    cust_name = models.CharField(max_length=255, blank=True, null=True)
    cas_ins_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'bank_case'


class CustData(models.Model):
    business_type = models.CharField(max_length=255)
    group = models.CharField(max_length=255)
    call_method = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    fenan_num = models.CharField(max_length=255)
    ht_case = models.CharField(max_length=255)
    ht_money = models.CharField(max_length=255)
    fa_sum_money = models.CharField(max_length=255)
    today_pass = models.CharField(max_length=255)
    today_call = models.CharField(max_length=255)
    day_phone_time = models.CharField(max_length=255)
    day_pass_rate = models.CharField(max_length=255)
    month_pass_sum = models.CharField(max_length=255)
    month_sum = models.CharField(max_length=255)
    month_phone_time = models.CharField(max_length=255)
    month_pass_rate = models.CharField(max_length=255)
    report_time = models.CharField(max_length=255)
    update_time = models.DateTimeField()
    project_name = models.ForeignKey('UserAccount', models.DO_NOTHING, db_column='project_name')
    day_all_case = models.CharField(max_length=255, blank=True, null=True)
    day_all_pass = models.CharField(max_length=255, blank=True, null=True)
    month_all_case = models.CharField(max_length=255, blank=True, null=True)
    month_all_pass = models.CharField(max_length=255, blank=True, null=True)
    call_all_time = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cust_data'


class DialogueRecord(models.Model):
    id = models.BigAutoField(primary_key=True)
    call_date = models.CharField(max_length=32)
    project_name = models.CharField(max_length=255)
    call_type = models.IntegerField()
    call_time = models.DateTimeField()
    answer_time = models.DateTimeField(blank=True, null=True)
    hangup_time = models.DateTimeField(blank=True, null=True)
    answer_type = models.IntegerField()
    transfer_type = models.IntegerField()
    dialogue_duration = models.IntegerField()
    phone_number = models.CharField(max_length=16)
    relation_type = models.IntegerField()
    relation = models.CharField(max_length=64)
    create_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    cust_name = models.CharField(max_length=255, blank=True, null=True)
    group = models.CharField(max_length=255, blank=True, null=True)
    business_type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dialogue_record'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Spider(models.Model):
    id = models.BigAutoField(primary_key=True)
    tieba_name = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    author_name = models.CharField(max_length=255, blank=True, null=True)
    public_time = models.DateTimeField(blank=True, null=True)
    content = models.CharField(max_length=3000, blank=True, null=True)
    reply_name = models.CharField(max_length=255, blank=True, null=True)
    reply_time = models.DateTimeField(blank=True, null=True)
    reply_content = models.CharField(max_length=3000, blank=True, null=True)
    second_reply = models.CharField(max_length=3000, blank=True, null=True)
    reply_type = models.CharField(max_length=255, blank=True, null=True)
    content_type = models.CharField(max_length=255, blank=True, null=True)
    public_media = models.CharField(max_length=255, blank=True, null=True)
    project_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'spider'


class UserAccount(models.Model):
    project_name = models.CharField(primary_key=True, max_length=255)
    jd_name = models.CharField(max_length=255)
    pwd = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'user_account'
