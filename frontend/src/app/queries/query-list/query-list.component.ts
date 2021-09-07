import { Component, OnInit } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Identity } from 'src/app/models/identity.model';
import { Query } from 'src/app/models/query.model';
import { Suggestion } from 'src/app/models/suggestion.model';
import { ApiService } from 'src/app/services/api.service';

@Component({
  selector: 'app-query-list',
  templateUrl: './query-list.component.html',
  styleUrls: ['./query-list.component.scss'],
})
export class QueryListComponent implements OnInit {
  private _queries$ = new BehaviorSubject<Query[]>([]);
  readonly queries$ = this._queries$.asObservable();

  private _identities$ = new BehaviorSubject<Identity[]>([]);
  readonly identities$ = this._identities$.asObservable();

  constructor(private _api: ApiService) {}

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    this._api.getIdentities().subscribe((result) => {
      this._identities$.next(result);
      this._api.getQueries().subscribe((result) => this._queries$.next(result));
    });
  }

  compare(i1: Identity, i2: Identity): boolean {
    if (i1 && i2 && i1.id === i2.id) {
      return true;
    } else if (!i1 && !i2) {
      return true;
    } else {
      return false;
    }
  }

  confirm(query: Query, suggestion: Suggestion): void {
    this._api
      .confirmSuggestion(query, suggestion)
      .subscribe(() => this.refresh());
  }

  delete(query: Query, suggestion: Suggestion): void {
    this._api
      .deleteSuggestion(query, suggestion)
      .subscribe(() => this.refresh());
  }
}
