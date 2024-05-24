package com.example.helloworld;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {

    private EditText billAmountEditText;
        private EditText tipPercentageEditText;
            private TextView tipResultTextView;
                private Button calculateTipButton;

                    @Override
                        protected void onCreate(Bundle savedInstanceState) {
                                super.onCreate(savedInstanceState);
                                        setContentView(R.layout.activity_main);

                                                billAmountEditText = findViewById(R.id.bill_amount);
                                                        tipPercentageEditText = findViewById(R.id.tip_percentage);
                                                                tipResultTextView = findViewById(R.id.tip_result);
                                                                        calculateTipButton = findViewById(R.id.calculate_tip);

                                                                                calculateTipButton.setOnClickListener(new View.OnClickListener() {
                                                                                            @Override
                                                                                                        public void onClick(View v) {
                                                                                                                        calculateTip();
                                                                                                                                    }
                                                                                                                                            });
                                                                                                                                                }

                                                                                                                                                    private void calculateTip() {
                                                                                                                                                            String billAmountString = billAmountEditText.getText().toString();
                                                                                                                                                                    String tipPercentageString = tipPercentageEditText.getText().toString();

                                                                                                                                                                            if (!billAmountString.isEmpty() && !tipPercentageString.isEmpty()) {
                                                                                                                                                                                        double billAmount = Double.parseDouble(billAmountString);
                                                                                                                                                                                                    double tipPercentage = Double.parseDouble(tipPercentageString);
                                                                                                                                                                                                                double tip = billAmount * (tipPercentage / 100);
                                                                                                                                                                                                                            tipResultTextView.setText("Tip: $" + String.format("%.2f", tip));
                                                                                                                                                                                                                                    } else {
                                                                                                                                                                                                                                                tipResultTextView.setText("Please enter both fields.");
                                                                                                                                                                                                                                                        }
                                                                                                                                                                                                                                                            }
                                                                                                                                                                                                                                                            }