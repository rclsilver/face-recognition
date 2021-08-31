import { Component, OnInit, ViewChild } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Identity } from 'src/app/models/identity.model';
import { ApiService } from 'src/app/services/api.service';
import { WebcamComponent } from '../webcam/webcam.component';

@Component({
  selector: 'app-learn',
  templateUrl: './learn.component.html',
  styleUrls: ['./learn.component.scss'],
})
export class LearnComponent implements OnInit {
  private _identity$ = new BehaviorSubject<Identity | undefined>(undefined);
  private _identitities$ = new BehaviorSubject<Identity[]>([]);

  readonly identity$ = this._identity$.asObservable();
  readonly identities$ = this._identitities$.asObservable();

  @ViewChild(WebcamComponent) webcam?: WebcamComponent;

  constructor(private _api: ApiService) {}

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    this._api
      .getIdentities()
      .subscribe((identities) => this._identitities$.next(identities));
  }

  select(event: Event): void {
    const element = event.target as HTMLSelectElement;
    const search = this._identitities$.value.filter(
      (identity) => identity.id === element.value
    );

    if (search.length) {
      this._identity$.next(search[0]);
    } else {
      this._identity$.next(undefined);
    }
  }

  learn(): void {
    if (this.webcam) {
      this.webcam.takeSnapshot();
    }
  }

  onCapture(image: Blob): void {
    this._api.learn(this._identity$.value!, image).subscribe((result) => {
      console.log(result);
    });
  }
}
