import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TestWebcamComponent } from './test-webcam.component';

describe('TestWebcamComponent', () => {
  let component: TestWebcamComponent;
  let fixture: ComponentFixture<TestWebcamComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TestWebcamComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TestWebcamComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
