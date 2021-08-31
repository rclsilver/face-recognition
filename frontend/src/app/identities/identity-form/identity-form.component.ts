import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Identity } from 'src/app/models/identity.model';
import { ApiService } from 'src/app/services/api.service';

@Component({
  selector: 'app-identity-form',
  templateUrl: './identity-form.component.html',
  styleUrls: ['./identity-form.component.scss'],
})
export class IdentityFormComponent {
  private _current?: Identity;

  @Input() set identity(value: Identity | undefined) {
    this._current = value;

    if (value) {
      this.record.first_name = value.first_name;
      this.record.last_name = value.last_name;
    } else {
      this.record.first_name = '';
      this.record.last_name = '';
    }
  }

  @Output() submit = new EventEmitter<Identity>();

  record: Pick<Identity, 'first_name' | 'last_name'> = {
    first_name: '',
    last_name: '',
  };

  constructor(private _api: ApiService) {}

  submitForm(): void {
    const request = this._current
      ? this._api.updateIdentity(this._current, this.record)
      : this._api.createIdentity(this.record);

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
