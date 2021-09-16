import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { BehaviorSubject } from 'rxjs';
import { finalize } from 'rxjs/operators';
import { FaceEncoding } from 'src/app/models/face-encoding.model';
import { Identity } from 'src/app/models/identity.model';
import { ApiService } from 'src/app/services/api.service';

@Component({
  templateUrl: './identity-faces.component.html',
  styleUrls: ['./identity-faces.component.scss'],
})
export class IdentityFacesComponent implements OnInit {
  private _loading$ = new BehaviorSubject<boolean>(false);
  readonly loading$ = this._loading$.asObservable();

  private _identity$ = new BehaviorSubject<Identity | null>(null);
  readonly identity$ = this._identity$.asObservable();

  private _faces$ = new BehaviorSubject<FaceEncoding[]>([]);
  readonly faces$ = this._faces$.asObservable();

  constructor(private _route: ActivatedRoute, private _api: ApiService) {}

  ngOnInit(): void {
    this._route.params.subscribe((params) => {
      this._api
        .getIdentity({ id: params.id })
        .pipe(finalize(() => this.refresh()))
        .subscribe((identity) => this._identity$.next(identity));
    });
  }

  refresh(): void {
    if (this._identity$.value) {
      this._loading$.next(true);
      this._api
        .getIdentityFaces({ id: this._identity$.value.id })
        .pipe(finalize(() => this._loading$.next(false)))
        .subscribe((faces) => this._faces$.next(faces));
    }
  }

  delete(face: FaceEncoding): void {
    if (this._identity$.value) {
      this._api
        .deleteIdentityFace(this._identity$.value, face)
        .subscribe(() => this.refresh());
    }
  }

  clear(): void {
    if (this._identity$.value) {
      this._api
        .clearIdentity(this._identity$.value)
        .subscribe(() => this.refresh());
    }
  }
}
