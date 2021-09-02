import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CameraLiveComponent } from './camera-live.component';

describe('CameraLiveComponent', () => {
  let component: CameraLiveComponent;
  let fixture: ComponentFixture<CameraLiveComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CameraLiveComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CameraLiveComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
