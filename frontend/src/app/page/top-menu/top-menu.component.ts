import { Component } from '@angular/core';

@Component({
  selector: 'app-top-menu',
  templateUrl: './top-menu.component.html',
  styleUrls: ['./top-menu.component.scss'],
})
export class TopMenuComponent {
  readonly items = [
    {
      label: 'Identities',
      path: 'identities',
    },
    {
      label: 'Query',
      path: 'recognition/query',
    },
    {
      label: 'Learn',
      path: 'recognition/learn',
    },
  ];

  constructor() {}
}
