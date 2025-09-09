from django.contrib.auth import authenticate, login
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.db import connection
from FileMngmntApp.models import CustomTable,customFields
import re
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from datetime import datetime
from math import ceil
import openpyxl
from django.core.files.storage import FileSystemStorage
import tempfile
from openpyxl import load_workbook
from django.conf import settings


def home(request):
    return render(request,'home.html')

def is_userAdmin(user):
    return user.is_authenticated and user.is_staff and not user.is_superuser
        

def is_normal_user(user):
    return user.is_authenticated and not user.is_staff and not user.is_superuser


def custom_login(request):
 
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        print("USER After Auth :",user)
        
        if user is not None:
            
            login(request, user)
            
            if user.is_superuser:
                return redirect('/admin/')

            elif user.is_staff:
                return redirect('admin_dashboard')
            
            else:
                return redirect('user_profile')
            
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'login.html')


@login_required
@user_passes_test(is_userAdmin)
def user_admin(request):
    return render(request,'admin_dashboard.html')


@login_required
def upload_file(request):
    return render(request, 'upload.html')


@login_required
@user_passes_test(is_normal_user)
def user_profile(request):
    return render(request, 'user_profile.html')


# ADMIN VIEW'S

def sanitize_name(name):

    name = re.sub(r'\W+', '_', name.strip().lower())
    if not re.match(r'^[a-z_]', name):
        name = f"col_{name}"
    return name

@login_required
@user_passes_test(is_userAdmin)
def create_custom_table(request):

    if request.method == 'POST':
        
        table_name = request.POST.get('table_name')
        field_names = request.POST.getlist('field_name[]')
        field_types = request.POST.getlist('field_type[]')
        field_max_lengths = request.POST.getlist('max_length[]')

        if not table_name or not field_names or not field_types or len(field_names) != len(field_types):
            messages.error(request, 'Invalid form data')
            return redirect('create_table')
        
        table_name_sql=sanitize_name(table_name)
        field_NameType_sql=[]

        for name, type_ ,size in zip(field_names, field_types,field_max_lengths):
            
            safe_name=sanitize_name(name)
            if type_ == "TEXT":
                try:
                    max_len = int(size) if size else 255
                except ValueError:
                    max_len = 255

                sql_type = f"VARCHAR({max_len})"

            elif type_ == "INTEGER":
                sql_type = "INTEGER"

            elif type_ == "DATE":
                sql_type = "DATE"

            elif type_ == "BOOLEAN":
                sql_type = "BOOLEAN"

            else:
                sql_type = "TEXT"  # fallback

            field_NameType_sql.append(f"{safe_name} {sql_type}")

        
        fields_sql_query=", ".join(field_NameType_sql)

        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name_sql} (id SERIAL PRIMARY KEY, {fields_sql_query});"

        try:
            with connection.cursor() as cursor:
                cursor.execute(create_sql)
            
            Tabel=CustomTable.objects.create(
                
                display_name =table_name.strip(),
                table_name = table_name_sql,
                created_by=request.user
            )
            
            for fname, ftype,max_len in zip(field_names, field_types,field_max_lengths):
                
                customFields.objects.create(

                    table =Tabel, 
                    display_name =fname.strip(),  # Original name
                    field_name = sanitize_name(fname),# Safe name
                    field_type = ftype,
                    max_length=int(max_len) if "VARCHAR" in ftype and max_len else None
                )

            messages.success(request, f"Table '{table_name}' created successfully.")


        except Exception as e:
            
            messages.error(request, f"Error creating table: {str(e)}")

        return redirect('create_table')

    return render(request, 'create_table.html')



@login_required
def view_staff_created_models(request):

    staff_users = User.objects.filter(is_staff=True, is_superuser=False)
    tables = CustomTable.objects.prefetch_related('fields').filter(created_by__in=staff_users)

    return render(request, 'view_tables.html', {'tables': tables})

@login_required
def get_table_fields(request,table_id):
    
    print("GET TABLE FIELDS CALLED !")
    table=get_object_or_404(CustomTable,id=table_id)
    fields=list(table.fields.values_list('field_name',flat=True))

    print(f'fields : {fields}')
    return JsonResponse({"fields":fields})


@login_required
def drop_table(request,table_id):

    table=get_object_or_404(CustomTable,id=table_id,created_by=request.user)
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {table.table_name}")
        table.delete()  # Remove metadata

        messages.success(request, f"Table '{table.display_name}' deleted.")
    except Exception as e:
        messages.error(request, f"Error deleting table: {str(e)}")

    return redirect('view_tables')


def view_table_data(request, table_name):
    
    table = get_object_or_404(CustomTable, table_name=table_name)
    row_limit=int(request.GET.get("limit",10))
    page_number=int(request.GET.get("page",1))
    
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        total_rows=cursor.fetchone()[0]
    print("Total No Row's :",total_rows)


    with connection.cursor() as cursor:
        cursor.execute(f'SELECT * FROM "{table_name}" ORDER BY id')
        columns = [col[0] for col in cursor.description]  # Get column names
        all_rows = [dict(zip(columns, row)) for row in cursor.fetchall()]  # Convert each row to dict
    
    display_columns = [col for col in columns if col.lower() != 'id']
    
    paginator=Paginator(all_rows,row_limit)
    page_obj=paginator.get_page(page_number)

    rows=list(page_obj.object_list)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":

        print("Row :",rows)
        print("Colum : ",columns)
        print("\n\n")
        print("No.of Pages :",paginator.num_pages)
        print("Curent Page : ",page_obj.number)

        return JsonResponse({

            "rows": rows,
            "columns": display_columns,
            'limit':row_limit,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,

        })


    context = {
        'table': table,
        'columns': display_columns,
        'rows': rows,
        'limit':row_limit,
        'page_obj': page_obj,
        "total_pages": paginator.num_pages,
    }
    
    return render(request, 'view_table_data.html', context)


@csrf_exempt
def update_table_data(request, table_name):
    
    if request.method == 'POST':

        try:
            data = json.loads(request.body)
            rows = data.get('rows', [])
            print("Rows >>> ",rows)

            with connection.cursor() as cursor:
                  
                for row in rows:

                    row_id = int(row.pop('id', None))
                    
                    # CHECK FOR DATE FORMATED DATA 
                    for column,data in row.items():
                        if isinstance(data,str) and "-" in data:
                            try:
                                parsed_date = datetime.strptime(data, "%d-%m-%Y").strftime("%Y-%m-%d")
                                row[column] = parsed_date
                            except ValueError:
                                pass  # Ignore if not a date                   
                    
                    if row_id:
                            
                        print(f"Row Id {row_id} >>> CONDTIONS {row_id > 0} ")
                        if row_id and int(row_id) > 0:    
   
                            #print("ROw id >> ", row_id)
                            #FORMATE THE DATE COLUMN DATA
                            for column,data in row.items():
                                if isinstance(data,str) and "-" in data:
                                    try:

                                        parsed_date = datetime.strptime(data, "%d-%m-%Y").strftime("%Y-%m-%d")
                                        row[column] = parsed_date

                                    except ValueError:
                                        pass  # Ignore if not a date


                            set_clauses = ', '.join([f'"{field}" = %s' for field in row.keys()])
                            values = list(row.values()) + [row_id]
                            #values.append(row_id)

                            sql = f'UPDATE "{table_name}" SET {set_clauses} WHERE id = %s'
                            cursor.execute(sql, values)

                        else:
                            
                            cursor.execute(f""" SELECT setval(
                                        pg_get_serial_sequence('"{table_name}"', 'id'),
                                        COALESCE(MAX(id), 0) + 1,
                                        false
                                        ) FROM "{table_name}"; """)                

                            column_clause = ", ".join([f'"{column}"' for column in row.keys()])  
                            column_data=list(row.values())
                            
                            value_clause = ", ".join(['%s']*len(row))
                            
                            Query_sql=f'INSERT INTO "{table_name}" ({column_clause}) VALUES ({value_clause})'

                            cursor.execute(Query_sql,column_data)
                
                # # ✅ Fix sequence after inserts (important for avoiding duplicate key errors)
                # cursor.execute(f"""
                #     SELECT setval(
                #         pg_get_serial_sequence('"{table_name}"', 'id'),
                #         COALESCE(MAX(id), 0) + 1,
                #         false
                #     ) FROM "{table_name}";
                # """)

            return JsonResponse({'success': True})
        
        except Exception as e:
            print("Update Error:", e)
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def view_row_data(request, table_name, row_id):

    row={}
    print("VIEW CALLED ")
    with connection.cursor() as cursor:
        
        cursor.execute(f'SELECT * FROM {table_name} LIMIT 0')
        columns = [col[0] for col in cursor.description]

    with connection.cursor() as cursor:
        
        if int(row_id) > 0:
            cursor.execute(f'SELECT * FROM "{table_name}" WHERE id = %s', [row_id])
            columns = [col[0] for col in cursor.description]
            print("ROW ID :",row_id)
            row = dict(zip(columns, cursor.fetchone()))

    display_columns = [col for col in columns if col.lower() != 'id']

    print("Display Column :",display_columns)
    return render(request, "view_row_detail.html",{
        "row": row,
        "columns": display_columns,
        "table_name":table_name,
        "row_id":row_id
        })


@csrf_exempt
def delete_table_row(request, table_name):
    
    if request.method == "POST":
        try:
            data=json.loads(request.body)
            uniqueRowId=data.get("id")

            print(f"Data : {data}")
            with connection.cursor() as cursor:
                Delquery=f'DELETE FROM "{table_name}" WHERE id= %s'
                cursor.execute(Delquery, [uniqueRowId])
            return JsonResponse({'success': True})
        
        except Exception as e:
            return JsonResponse({"success":False,'error':str(e)})
    

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


#USER VIEW'S

def choose_table_and_upload(request):
    
    headers = []
    preview_rows = []
    rows_inserted = 0
    missing_headers = []
    extra_headers = []
    selected_table = None
    sheets=[]
    Selected_sheet=None


    tables = CustomTable.objects.all()

    try:
        if request.method == 'POST':
            table_id = request.POST.get('table_id')
            selected_table = get_object_or_404(CustomTable, id=table_id)

            print(f'Get FIle Condition : >> {request.FILES.get('excel_file')}')
            if request.FILES.get('excel_file'):

                excel_file = request.FILES['excel_file']
                fs = FileSystemStorage(location=settings.UPLOADS_DIR)
                filename = fs.save(excel_file.name, excel_file)

                file_path = fs.path(filename)

                # Save file path in session for later use
                # request.session['uploaded_excel_path'] = file_path
                request.session['uploaded_excel_path'] = f"uploads/{filename}"
                
            else:
                # No new file uploaded → try to get the saved one
                relative_path = request.session.get('uploaded_excel_path')
                print("Fetch From Session :(file Path ) ",relative_path)

                
                if not relative_path:
                    return render(request, 'choose_table.html', {
                        'tables': tables,
                        'error': 'No file uploaded or file missing.'
                    })
                
                file_path = os.path.join(settings.MEDIA_ROOT, relative_path)
                if not os.path.exists(file_path):
                    return render(request, 'choose_table.html', {
                            'tables': tables,
                            'error': 'File missing.'
                    })
                          
            print("Excel file :",file_path)

            # Load workbook
            wb = load_workbook(file_path)
            sheets=list(wb.sheetnames)

            Selected_sheet = request.POST.get('sheet_name')
            print("Selected Sheet >> ",Selected_sheet)
            if not Selected_sheet:
                Selected_sheet=sheets[0]

            Active_sheet =wb[Selected_sheet] 
            # Excel headers
            headers = [str(cell.value).strip() if cell.value else "" 
                       for cell in next(Active_sheet.iter_rows(min_row=1, max_row=1))]
            
            # Required headers from DB
            required_headers = list(selected_table.fields.values_list('display_name', flat=True))
            db_sanitized_headers=list(selected_table.fields.values_list('field_name', flat=True))

            # CREATE A LOOK UP
            header_lookup = dict(zip(required_headers, db_sanitized_headers))
            print("Header's And there Sanitized Name : ",header_lookup)

            # Check missing and extra headers
            missing_headers = [req for req in required_headers if req not in headers]
            
            extra_headers = [h for h in headers if h not in required_headers]
            
            # Only use matching headers
            matching_headers = [h for h in headers if h in required_headers]
            
            # Preview first 5 rows
            preview_rows = list(Active_sheet.iter_rows(min_row=2, values_only=True))[:5]
            print("Matching Headers : >>>> ",matching_headers)
            # Insert if confirmed and no missing headers

            if "confirm_insert" in request.POST and not missing_headers:
                data_rows = []
    
                for row in Active_sheet.iter_rows(min_row=2, values_only=True):
                    # Keep only matching columns
                    filtered_row = [row[headers.index(h)] for h in matching_headers]
                    data_rows.append(filtered_row)
                    
                    if data_rows:
                        print("Data Row >>>>>>>>>>> ",data_rows)
                        # Format date columns if needed
                        for r_index, r in enumerate(data_rows):
                            for c_index, val in enumerate(r):
                                if isinstance(val, str) and "-" in val:
                                    try:
                                        data_rows[r_index][c_index] = datetime.strptime(val, "%d-%m-%Y").strftime("%Y-%m-%d")
                                    except ValueError:
                                        pass

                        # for column, value in row.items():
                        #     if isinstance(value, str) and "-" in value:
                        #         try:
                        #             parsed_date = datetime.strptime(value, "%d-%m-%Y").strftime("%Y-%m-%d")
                        #             row[column] = parsed_date
                        #         except ValueError:
                        #             pass  # Ignore if not a valid date

                print("-------------// Esatablish A connnection After Collecting Excel Data //----------")
                with connection.cursor() as cursor:
                    
                    sanitized_Matching_headers=[header_lookup[matched_header] for matched_header in matching_headers]
                    print("Sanitized Headder in sql ",sanitized_Matching_headers)

                    placeholders = ", ".join(["%s"] * len(sanitized_Matching_headers))
                    col_names = ", ".join([f'"{col}"' for col in sanitized_Matching_headers])
                    sql = f'INSERT INTO "{selected_table.table_name}" ({col_names}) VALUES ({placeholders})'
                            
                    cursor.executemany(sql, data_rows)
                    rows_inserted = len(data_rows)

                print(" Rows inserted:", rows_inserted)

    except Exception as e:
        print("Error:", (e))

    return render(request, 'choose_table.html', {
        'tables': tables,
        'headers': headers,
        'preview_rows': preview_rows,
        'selected_table': selected_table,
        'rows_inserted': rows_inserted,
        'missing_headers': missing_headers,
        'extra_headers': extra_headers,
        'sheets':sheets,
        'selected_sheet':Selected_sheet
    })


def get_sheet_names(request):

    sheet_names=[]
    
    print("Excel FIle Exists :",request.FILES.get("excel_file"))

    if request.method == 'POST' and request.FILES.get("excel_file"):
        
        excel_file=request.FILES['excel_file']

        if not excel_file.name.endswith(('.xlsx', '.xlsm')):
            return JsonResponse({"error": "Only .xlsx or .xlsm files are supported"}, status=400)

        fs=FileSystemStorage(location=settings.UPLOADS_DIR)
        savefile_fs=fs.save(excel_file.name,excel_file)
        excel_file_path=fs.path(savefile_fs)

    
        # with tempfile.NamedTemporaryFile(delete=False) as temp:

        #     for chunk in excel_file.chunks():
        #         temp.write(chunk)
        #     temp_path=temp.name
        
        print("temp_path :>>",excel_file_path)
        

        workbook = load_workbook(excel_file_path, read_only=True)
        sheet_names = workbook.sheetnames
        print("SHEET NAME :",sheet_names)
        workbook.close()
        return JsonResponse({"sheet_names":sheet_names})
    
    return JsonResponse({"error": "No file uploaded"}, status=400)