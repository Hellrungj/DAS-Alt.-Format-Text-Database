from app.allImports import *
from app.logic.switch import switch
from flask import flash, url_for
import flask_admin as admin
from flask_admin import form
from flask_admin.contrib.peewee import ModelView
from flask_admin import BaseView, expose
from flask_security import Security, roles_accepted, login_required, current_user
from flask_admin.form import rules
from flask_admin.base import AdminIndexView
import datetime

class MyHomeView(AdminIndexView):
    @login_required
    @roles_accepted("Admin")
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

admin = admin.Admin(app, index_view=MyHomeView(), name='DAS Admin')
#path = op.join(op.dirname(__file__), 'static/files/uploads')

class UserAdmin(ModelView):
    def is_accessible(self):
        return current_user.has_role('Admin')
    # Visible columns in the list view
    column_exclude_list = ['text']
    # List of columns that can be sorted. For 'user' column, use User.email as
    # a column.
    column_sortable_list = ('username', 'email', 'password', '')
    # Full text search
    column_searchable_list = ('username', 'email')
    # Column filters
    column_filters = ('username', 'email')
    
    form_create_rules = [
        # Header and four fields. Email field will go above phone field.
        rules.FieldSet(('username', 'email', 'password'), 'Personal'),
        # Separate header and few fields
        rules.Header('Confirmation'),
        rules.Field('active'),
        # String is resolved to form field, so there's no need to explicitly use `rules.Field`
        'confirmed_at','notes'
        # Show macro from Flask-Admin lib.html (it is included with 'lib' prefix)
    ]
    # Use same rule set for edit page
    form_edit_rules = form_create_rules
    
class RoleAdmin(ModelView):
    def is_accessible(self):
        return current_user.has_role('Admin')
    # Visible columns in the list view
    column_exclude_list = ['text']
    
class UserRolesAdmin(ModelView):
    def is_accessible(self):
        return current_user.has_role('Admin')
    # Visible columns in the list view
    column_exclude_list = ['text']
    

class PostAdmin(ModelView):
    def is_accessible(self):
        return current_user.has_role('Admin')
    # Visible columns in the list view
    column_exclude_list = ['text']
    # List of columns that can be sorted. For 'user' column, use User.email as
    # a column.
    column_sortable_list = ('title', ('user', User.email), '')
    # Full text search
    column_searchable_list = ('title', User.username)
    # Column filters
    column_filters = ('title',
                      'date',
                      User.username)
    
class FileDataAdmin(ModelView):
    def is_accessible(self):
        return current_user.has_role('Admin')
    can_create = False
    # Visible columns in the list view
    column_exclude_list = ['text']
    # List of columns that can be sorted. For 'user' column, use User.email as
    # a column.
    column_sortable_list = ('title', 'author', 'edition',
                            'size', 'filename', 'file_type',
                            'created_at','last_modified',
                            ('last_modified_by',User.email),
                            'file_path', 'hidden')

    # Full text search
    column_searchable_list = ('title', User.username)
    # Column filters
    column_filters = ('title', 'author', 'edition',
                        'size', 'filename', 'file_type',
                        User.username,)
                        
class FileAdmin(BaseView):
    def is_accessible(self):
        return current_user.has_role('Admin')
    @login_required
    @expose('/')
    def AdminUpload(self):
        get_time = datetime.datetime.now()
        Day = get_time.strftime("%Y-%m-%d")
        result = File.select().where(File.last_modified_by == current_user.id)
        return self.render("admin/upload.html", cfg = cfg, items = result)

    @login_required
    @expose('/')
    def uploading(self):
      app.logger.info("Attempting to upload file.")
      ERROR = 0
      file = request.files['file']
      try:
        get_time = datetime.datetime.now()
        time_stamp = get_time.strftime("%Y-%m-%d")
        lastmodified = get_time.strftime("%Y-%m-%d %I:%M")
        filename = ('UploadedFile' + str(time_stamp) + "." + str(file.filename))
        directory_paths = "app/static/files/uploads/"
        if not os.path.exists(directory_paths):
                try:
                  os.makedirs(directory_paths)
                except OSError as e:
                  print e.errno
                  pass
                
        complete_path = (directory_paths + str(filename)).replace(" ", "")
        file.save(complete_path)
        app.logger.info("Upload file.")
        Exists = os.path.exists(complete_path)
        app.logger.info(("Exists: " + str(Exists)))
          
        data = File(  title     = file.filename,
                      author    = " ",
                      edition   = " ",
                      size      = " ",
                      filename  = filename,
                      file_type = str(file.filename.split(".").pop()),
                      created_at = time_stamp,
                      last_modified = lastmodified,
                      last_modified_by = current_user.id,
                      file_path = complete_path,
                      hidden    = 0)
        data.save()
        app.logger.info("Updated the database.")
      except:
        ERROR = 2  
              
      if ERROR == 0:
        return redirect('/upload',code=302)
      else:  
        if ERROR == 1: 
          message = "An error occured during the authentication process"
        else: 
          message = "An error occured during the upload process."
        return message                       
    
class AdminLogout(BaseView):
    @login_required
    @roles_accepted("Admin")
    @expose('/')
    def AdminLogout(self):
        return redirect('/logout')
        
class StudentView(BaseView):
    @login_required
    @roles_accepted("Admin")
    @expose('/')
    def StudentView(self):
        return redirect('/index')

admin.add_view(FileDataAdmin(File, name='FileData'))
admin.add_view(FileAdmin(name='FileUpload', endpoint="fileupload"))
admin.add_view(UserAdmin(User))
admin.add_view(RoleAdmin(Role))
admin.add_view(UserRolesAdmin(UserRole))
admin.add_view(StudentView(name='StudentView', endpoint='studentview'))
admin.add_view(AdminLogout(name='Logout', endpoint='logout'))