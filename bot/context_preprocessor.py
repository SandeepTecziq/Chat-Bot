from .forms import ChangePasswordForm
from .view_functions import get_all_detail, check_trained_status


def form_preprocessor(request):
    change_password_form = ChangePasswordForm()

    context = {
        'change_password_form': change_password_form,
    }

    return context


def admin_variables(request):
    if request.user.is_authenticated and request.user.role == 'admin' and request.user.is_superuser is False:
        secret_key = request.user.company.secret_key
        company, note_number, notification, employees = get_all_detail(secret_key)
        all_saved = check_trained_status(secret_key)
        parent_company = request.user.company
        context = {
            'secret_key': secret_key,
            'company_qry': company,
            'notification': notification,
            'note_number': note_number,
            'all_saved': all_saved,
            'parent_company': parent_company,
            'employees': employees,
            'parent_secret_key': parent_company.secret_key,
        }

    else:
        context = {

        }

    return context

