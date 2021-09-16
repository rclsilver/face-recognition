import { ComponentFixture, TestBed } from '@angular/core/testing';

import { IdentityFacesComponent } from './identity-faces.component';

describe('IdentityFacesComponent', () => {
  let component: IdentityFacesComponent;
  let fixture: ComponentFixture<IdentityFacesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ IdentityFacesComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(IdentityFacesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
