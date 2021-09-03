import { Component, EventEmitter, Input, Output } from '@angular/core';
import { User } from 'src/app/models/user.model';
import { ApiService } from 'src/app/services/api.service';

@Component({
  selector: 'app-user-form',
  templateUrl: './user-form.component.html',
  styleUrls: ['./user-form.component.scss'],
})
export class UserFormComponent {
  private _current?: User;

  @Input() set user(value: User | undefined) {
    this._current = value;

    if (value) {
      this.record.username = value.username;
      this.record.is_admin = value.is_admin;
    } else {
      this.record.username = '';
      this.record.is_admin = false;
    }
  }

  @Output() submit = new EventEmitter<User>();

  record: Pick<User, 'username' | 'is_admin'> = {
    username: '',
    is_admin: false,
  };

  constructor(private _api: ApiService) {}

  get isNew(): boolean {
    return !!this._current?.id
  }

  submitForm(): void {
    const request = this._current
      ? this._api.updateUser(this._current, {
          is_admin: this.record.is_admin,
        })
      : this._api.createUser(this.record);

    request.subscribe(
      (result) => {
        this.submit.emit(result);
      },
      (error) => {
        console.error(error);
      }
    );
  }
}
