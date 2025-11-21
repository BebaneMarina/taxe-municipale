import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RecapTransactionComponent } from './recap-transaction.component';

describe('RecapTransactionComponent', () => {
  let component: RecapTransactionComponent;
  let fixture: ComponentFixture<RecapTransactionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RecapTransactionComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RecapTransactionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
