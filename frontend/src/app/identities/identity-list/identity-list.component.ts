import { Component, OnInit, ViewChild } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Identity } from 'src/app/models/identity.model';
import { ApiService } from 'src/app/services/api.service';
import { IdentityFormComponent } from '../identity-form/identity-form.component';

@Component({
  selector: 'app-identity-list',
  templateUrl: './identity-list.component.html',
  styleUrls: ['./identity-list.component.scss'],
})
export class IdentityListComponent implements OnInit {
  private _identities$ = new BehaviorSubject<Identity[]>([]);
  readonly identities$ = this._identities$.asObservable();

  private _form$ = new BehaviorSubject<boolean>(false);
  readonly form$ = this._form$.asObservable();

  @ViewChild('form') form?: IdentityFormComponent;

  constructor(private _api: ApiService) {}

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    // Refresh the list
    this._api
      .getIdentities()
      .subscribe((identities) => this._identities$.next(identities));

    // Hide the form
    this._form$.next(false);
  }

  edit(identity?: Identity): void {
    this.form!.identity = identity;
    this._form$.next(true);
  }

  delete(identity: Identity): void {
    this._api.deleteIdentity(identity).subscribe(() => this.refresh());
  }
}
