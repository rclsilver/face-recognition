import { Component, OnInit, ViewChild } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { User } from 'src/app/models/user.model';
import { ApiService } from 'src/app/services/api.service';

@Component({
  selector: 'app-user-list',
  templateUrl: './user-list.component.html',
  styleUrls: ['./user-list.component.scss'],
})
export class UserListComponent implements OnInit {
  private _users$ = new BehaviorSubject<User[]>([]);
  readonly users$ = this._users$.asObservable();

  private _form$ = new BehaviorSubject<boolean>(false);
  readonly form$ = this._form$.asObservable();

  constructor(private _api: ApiService) {}

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    // Refresh the list
    this._api.getUsers().subscribe((users) => this._users$.next(users));

    // Hide the form
    this._form$.next(false);
  }

  delete(user: User): void {
    this._api.deleteUser(user).subscribe(() => this.refresh());
  }
}
