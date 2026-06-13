package enc.icssoftwares.com.vakkiampro;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.DatePickerDialog;
import android.app.Dialog;
import android.app.TimePickerDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.graphics.Typeface;
import android.net.wifi.WifiManager;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.telephony.TelephonyManager;
import android.text.Html;
import android.text.method.LinkMovementMethod;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.DatePicker;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.TimePicker;
import android.widget.Toast;
import java.util.Calendar;
/* loaded from: classes.dex */
public class InputActivity extends Activity {
    int A;
    int B;
    int C;
    ah E;
    al F;

    /* renamed from: a  reason: collision with root package name */
    EditText f585a;
    EditText b;
    EditText c;
    Button d;
    Button e;
    Button f;
    Button g;
    Button h;
    Button i;
    Button j;
    TextView k;
    TextView l;
    TextView m;
    TextView n;
    TextView o;
    TextView p;
    TextView q;
    TextView r;
    TextView s;
    TextView t;
    TextView u;
    TextView v;
    TextView w;
    TextView x;
    int y;
    int z;
    boolean D = false;
    private DatePickerDialog.OnDateSetListener G = new DatePickerDialog.OnDateSetListener() { // from class: enc.icssoftwares.com.vakkiampro.InputActivity.4
        @Override // android.app.DatePickerDialog.OnDateSetListener
        public final void onDateSet(DatePicker datePicker, int i, int i2, int i3) {
            InputActivity inputActivity = InputActivity.this;
            inputActivity.y = i;
            inputActivity.z = i2;
            inputActivity.A = i3;
            inputActivity.d();
        }
    };
    private TimePickerDialog.OnTimeSetListener H = new TimePickerDialog.OnTimeSetListener() { // from class: enc.icssoftwares.com.vakkiampro.InputActivity.5
        @Override // android.app.TimePickerDialog.OnTimeSetListener
        public final void onTimeSet(TimePicker timePicker, int i, int i2) {
            InputActivity inputActivity = InputActivity.this;
            inputActivity.B = i;
            inputActivity.C = i2;
            inputActivity.e();
        }
    };

    private String a(int i) {
        return getResources().getStringArray(C0023R.array.planets_short)[i];
    }

    private String a(TelephonyManager telephonyManager) {
        String deviceId = telephonyManager.getDeviceId();
        if (deviceId == null) {
            String string = Build.SERIAL != "unknown" ? Build.SERIAL : Settings.Secure.getString(getContentResolver(), "android_id");
            return "       " + string.trim().substring(0, 8);
        }
        switch (telephonyManager.getPhoneType()) {
            case 0:
                return f();
            case 1:
            case 2:
                return deviceId;
            default:
                return "UNKNOWN: ID=".concat(String.valueOf(deviceId));
        }
    }

    private String b(int i) {
        return getResources().getStringArray(C0023R.array.inputscreen)[i];
    }

    /* JADX INFO: Access modifiers changed from: private */
    public void d() {
        EditText editText = this.f585a;
        StringBuilder sb = new StringBuilder();
        sb.append(this.A);
        sb.append("/");
        sb.append(this.z + 1);
        sb.append("/");
        sb.append(this.y);
        sb.append(" ");
        editText.setText(sb);
    }

    /* JADX INFO: Access modifiers changed from: private */
    public void e() {
        EditText editText = this.b;
        StringBuilder sb = new StringBuilder();
        sb.append(this.B);
        sb.append(":");
        sb.append(this.C);
        sb.append(":00");
        editText.setText(sb);
    }

    private String f() {
        String str;
        WifiManager wifiManager = (WifiManager) getSystemService("wifi");
        if (wifiManager.isWifiEnabled()) {
            str = wifiManager.getConnectionInfo().getMacAddress();
        } else {
            wifiManager.setWifiEnabled(true);
            String macAddress = wifiManager.getConnectionInfo().getMacAddress();
            wifiManager.setWifiEnabled(false);
            str = macAddress;
        }
        String replaceAll = str.replaceAll(":", "");
        return "7654321" + replaceAll.substring(4).toUpperCase();
    }

    public final void a() {
        View inflate = LayoutInflater.from(this).inflate(C0023R.layout.regdlg, (ViewGroup) null);
        TextView textView = (TextView) inflate.findViewById(C0023R.id.message);
        final EditText editText = (EditText) inflate.findViewById(C0023R.id.EditText_ID);
        String a2 = a((TelephonyManager) getSystemService("phone"));
        ((TextView) inflate.findViewById(C0023R.id.MobileID)).setText("Mobile ID: V" + a2.substring(7));
        String string = getResources().getString(C0023R.string.my_str1);
        String string2 = getResources().getString(C0023R.string.my_str2);
        String string3 = getResources().getString(C0023R.string.my_str3);
        String string4 = getResources().getString(C0023R.string.my_str4);
        String string5 = getResources().getString(C0023R.string.my_str5);
        String string6 = getResources().getString(C0023R.string.my_str6);
        textView.setClickable(true);
        textView.setLinkTextColor(-16776961);
        textView.setMovementMethod(LinkMovementMethod.getInstance());
        textView.setText(Html.fromHtml(string + "<br><br>" + string2 + "<br><br>" + string3 + "<br><br>" + string4 + "<br><br>" + string5 + "<br><br>" + string6));
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Activation");
        builder.setIcon(C0023R.drawable.ic_launcher);
        builder.setView(inflate);
        builder.setCancelable(true);
        builder.setInverseBackgroundForced(false);
        builder.setPositiveButton("Activate", new DialogInterface.OnClickListener() { // from class: enc.icssoftwares.com.vakkiampro.InputActivity.2
            @Override // android.content.DialogInterface.OnClickListener
            public final void onClick(DialogInterface dialogInterface, int i) {
                String obj = editText.getText().toString();
                System.out.println("Password is=".concat(String.valueOf(obj)));
                new c();
                c.a("vakreg", InputActivity.this.getApplicationContext(), obj);
            }
        });
        builder.setNegativeButton("Cancel", new DialogInterface.OnClickListener() { // from class: enc.icssoftwares.com.vakkiampro.InputActivity.3
            @Override // android.content.DialogInterface.OnClickListener
            public final void onClick(DialogInterface dialogInterface, int i) {
            }
        });
        builder.create().show();
    }

    /* JADX WARN: Code restructure failed: missing block: B:67:0x0631, code lost:
        if (r11 != false) goto L120;
     */
    /* JADX WARN: Code restructure failed: missing block: B:69:0x0634, code lost:
        if (r11 != false) goto L123;
     */
    /* JADX WARN: Code restructure failed: missing block: B:71:0x0637, code lost:
        if (r11 != false) goto L126;
     */
    /* JADX WARN: Code restructure failed: missing block: B:73:0x063a, code lost:
        if (r11 == false) goto L128;
     */
    /* JADX WARN: Code restructure failed: missing block: B:75:0x063d, code lost:
        r6 = 3;
     */
    /* JADX WARN: Code restructure failed: missing block: B:76:0x063f, code lost:
        if (r11 != false) goto L122;
     */
    /* JADX WARN: Code restructure failed: missing block: B:77:0x0641, code lost:
        r6 = 4;
     */
    /* JADX WARN: Code restructure failed: missing block: B:78:0x0643, code lost:
        r6 = 7;
     */
    /* JADX WARN: Code restructure failed: missing block: B:79:0x0645, code lost:
        if (r11 != false) goto L125;
     */
    /* JADX WARN: Code restructure failed: missing block: B:80:0x0647, code lost:
        r6 = 5;
     */
    /* JADX WARN: Code restructure failed: missing block: B:81:0x0649, code lost:
        r6 = 1;
     */
    /* JADX WARN: Code restructure failed: missing block: B:82:0x064b, code lost:
        if (r11 != false) goto L128;
     */
    /* JADX WARN: Code restructure failed: missing block: B:83:0x064d, code lost:
        r6 = 6;
     */
    /* JADX WARN: Code restructure failed: missing block: B:84:0x064f, code lost:
        r6 = 2;
     */
    /*
        Code decompiled incorrectly, please refer to instructions dump.
        To view partially-correct add '--show-bad-code' argument
    */
    public final void b() {
        /*
            Method dump skipped, instructions count: 2682
            To view this dump add '--comments-level debug' option
        */
        throw new UnsupportedOperationException("Method not decompiled: enc.icssoftwares.com.vakkiampro.InputActivity.b():void");
    }

    public final String c() {
        return a((TelephonyManager) getSystemService("phone")).substring(7);
    }

    @Override // android.app.Activity
    protected void onActivityResult(int i, int i2, Intent intent) {
        if (i2 == -1) {
            if (!intent.hasExtra("city")) {
                String[] split = intent.getExtras().getString("opened").toString().split("``");
                this.c.setText(split[0]);
                this.f585a.setText(split[1]);
                this.b.setText(split[2]);
                this.w.setText(split[3]);
                this.k.setText(split[4]);
                this.l.setText(split[5]);
                this.m.setText(split[6]);
                this.n.setText(split[7]);
                return;
            }
            String stringExtra = intent.getStringExtra("city");
            if (stringExtra.length() > 3) {
                String[] split2 = stringExtra.split(":");
                this.x.setText(split2[0]);
                this.w.setText(split2[0]);
                this.k.setText(split2[1]);
                this.l.setText(split2[2]);
                this.m.setText(split2[3]);
                this.n.setText("0.0.E");
            }
        }
    }

    @Override // android.app.Activity
    public void onCreate(Bundle bundle) {
        super.onCreate(bundle);
        setContentView(C0023R.layout.input);
        this.f585a = (EditText) findViewById(C0023R.id.txt_DOB);
        this.b = (EditText) findViewById(C0023R.id.txt_TOB);
        this.c = (EditText) findViewById(C0023R.id.tbl_txtName);
        this.w = (TextView) findViewById(C0023R.id.autocomplete_country);
        this.x = (TextView) findViewById(C0023R.id.textPlace);
        this.k = (EditText) findViewById(C0023R.id.txt_LATI);
        this.l = (EditText) findViewById(C0023R.id.txt_LONGI);
        this.m = (EditText) findViewById(C0023R.id.txt_STD);
        this.n = (EditText) findViewById(C0023R.id.txt_DST);
        new c();
        String a2 = c.a(getApplicationContext(), "Place");
        if (a2.trim().length() != 0) {
            this.w.setText(a2);
            this.k.setText(c.a(getApplicationContext(), "Lati"));
            this.l.setText(c.a(getApplicationContext(), "Longi"));
            this.m.setText(c.a(getApplicationContext(), "std"));
            this.n.setText(c.a(getApplicationContext(), "dst"));
        }
        this.d = (Button) findViewById(C0023R.id.btn_DOB);
        this.e = (Button) findViewById(C0023R.id.btn_TOB);
        this.f = (Button) findViewById(C0023R.id.btn_Result);
        this.g = (Button) findViewById(C0023R.id.btn_dPlace);
        this.h = (Button) findViewById(C0023R.id.btn_pdf1);
        this.i = (Button) findViewById(C0023R.id.btn_Save);
        this.j = (Button) findViewById(C0023R.id.btn_Open);
        this.E = new ah();
        this.F = new al();
        this.o = (TextView) findViewById(C0023R.id.txtHIname);
        this.p = (TextView) findViewById(C0023R.id.txtHIdob);
        this.q = (TextView) findViewById(C0023R.id.txtHItob);
        this.r = (TextView) findViewById(C0023R.id.txtHIplace);
        this.s = (TextView) findViewById(C0023R.id.txtHIlati);
        this.t = (TextView) findViewById(C0023R.id.txtHIlongi);
        this.u = (TextView) findViewById(C0023R.id.txtHItzone);
        this.v = (TextView) findViewById(C0023R.id.txtHIdst);
        this.o.setText(b(0));
        this.p.setText(b(1));
        this.q.setText(b(2));
        this.r.setText(b(3));
        this.s.setText(b(4));
        this.t.setText(b(5));
        this.u.setText(b(6));
        this.v.setText(b(7));
        this.f.setText(b(8));
        Typeface createFromAsset = Typeface.createFromAsset(getAssets(), "fonts/DAWN-110.TTF");
        this.o.setTypeface(createFromAsset);
        this.p.setTypeface(createFromAsset);
        this.q.setTypeface(createFromAsset);
        this.r.setTypeface(createFromAsset);
        this.s.setTypeface(createFromAsset);
        this.t.setTypeface(createFromAsset);
        this.u.setTypeface(createFromAsset);
        this.v.setTypeface(createFromAsset);
        this.f.setTypeface(createFromAsset);
        Calendar calendar = Calendar.getInstance();
        this.y = calendar.get(1);
        this.z = calendar.get(2);
        this.A = calendar.get(5);
        this.B = calendar.get(11);
        this.C = calendar.get(12);
        this.f.setEnabled(true);
        d();
        e();
        this.d.setOnClickListener(new View.OnClickListener() { // from class: enc.icssoftwares.com.vakkiampro.InputActivity.1
            @Override // android.view.View.OnClickListener
            public final void onClick(View view) {
                InputActivity.this.showDialog(0);
                InputActivity.this.f.setEnabled(true);
            }
        });
        this.e.setOnClickListener(new View.OnClickListener() { // from class: enc.icssoftwares.com.vakkiampro.InputActivity.6
            @Override // android.view.View.OnClickListener
            public final void onClick(View view) {
                InputActivity.this.showDialog(999);
                InputActivity.this.f.setEnabled(true);
            }
        });
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setCancelable(true);
        builder.setTitle("Trial Version");
        builder.setInverseBackgroundForced(false);
        builder.setMessage("Limited to 2019 only. Register with us for full functionality...");
        builder.setPositiveButton("Yes", new DialogInterface.OnClickListener() { // from class: enc.icssoftwares.com.vakkiampro.InputActivity.7
            @Override // android.content.DialogInterface.OnClickListener
            public final void onClick(DialogInterface dialogInterface, int i) {
            }
        });
        this.g.setOnClickListener(new View.OnClickListener() { // from class: enc.icssoftwares.com.vakkiampro.InputActivity.8
            @Override // android.view.View.OnClickListener
            public final void onClick(View view) {
                new c();
                c.a(InputActivity.this.getApplicationContext(), "Place", InputActivity.this.w.getText().toString());
                c.a(InputActivity.this.getApplicationContext(), "Lati", InputActivity.this.k.getText().toString());
                c.a(InputActivity.this.getApplicationContext(), "Longi", InputActivity.this.l.getText().toString());
                c.a(InputActivity.this.getApplicationContext(), "std", InputActivity.this.m.getText().toString());
                c.a(InputActivity.this.getApplicationContext(), "dst", InputActivity.this.n.getText().toString());
                Toast.makeText(InputActivity.this.getApplicationContext(), "Default Place Saved..", 0).show();
            }
        });
        this.w.setOnClickListener(new View.OnClickListener() { // from class: enc.icssoftwares.com.vakkiampro.InputActivity.9
            @Override // android.view.View.OnClickListener
            public final void onClick(View view) {
                InputActivity.this.startActivityForResult(new Intent(InputActivity.this, PlacesActivity.class), 1);
            }
        });
        this.f.setOnClickListener(new View.OnClickListener() { // from class: enc.icssoftwares.com.vakkiampro.InputActivity.10
            /* JADX WARN: Removed duplicated region for block: B:22:0x00af  */
            /* JADX WARN: Removed duplicated region for block: B:28:0x00e2 A[ADDED_TO_REGION] */
            @Override // android.view.View.OnClickListener
            /*
                Code decompiled incorrectly, please refer to instructions dump.
                To view partially-correct add '--show-bad-code' argument
            */
            public final void onClick(android.view.View r10) {
                /*
                    Method dump skipped, instructions count: 385
                    To view this dump add '--comments-level debug' option
                */
                throw new UnsupportedOperationException("Method not decompiled: enc.icssoftwares.com.vakkiampro.InputActivity.AnonymousClass10.onClick(android.view.View):void");
            }
        });
        this.h.setOnClickListener(new View.OnClickListener() { // from class: enc.icssoftwares.com.vakkiampro.InputActivity.11
            /* JADX WARN: Removed duplicated region for block: B:11:0x004f  */
            /* JADX WARN: Removed duplicated region for block: B:19:0x0094  */
            /* JADX WARN: Removed duplicated region for block: B:25:0x00c7 A[ADDED_TO_REGION] */
            /* JADX WARN: Removed duplicated region for block: B:29:0x013e  */
            /* JADX WARN: Removed duplicated region for block: B:33:? A[RETURN, SYNTHETIC] */
            @Override // android.view.View.OnClickListener
            /*
                Code decompiled incorrectly, please refer to instructions dump.
                To view partially-correct add '--show-bad-code' argument
            */
            public final void onClick(android.view.View r11) {
                /*
                    Method dump skipped, instructions count: 344
                    To view this dump add '--comments-level debug' option
                */
                throw new UnsupportedOperationException("Method not decompiled: enc.icssoftwares.com.vakkiampro.InputActivity.AnonymousClass11.onClick(android.view.View):void");
            }
        });
        this.j.setOnClickListener(new View.OnClickListener() { // from class: enc.icssoftwares.com.vakkiampro.InputActivity.12
            @Override // android.view.View.OnClickListener
            public final void onClick(View view) {
                InputActivity.this.startActivityForResult(new Intent(InputActivity.this, DataFileOpen.class), 1);
            }
        });
        this.i.setOnClickListener(new View.OnClickListener() { // from class: enc.icssoftwares.com.vakkiampro.InputActivity.13
            @Override // android.view.View.OnClickListener
            public final void onClick(View view) {
                Context applicationContext;
                String str;
                InputActivity inputActivity = InputActivity.this;
                String obj = inputActivity.c.getText().toString();
                if (obj.trim().length() <= 0) {
                    applicationContext = inputActivity.getApplicationContext();
                    str = "Enter Name!..";
                } else {
                    c.a("/ICS_VAK/", obj, inputActivity, (((((((obj + "``") + inputActivity.f585a.getText().toString() + "``") + inputActivity.b.getText().toString() + "``") + inputActivity.w.getText().toString() + "``") + inputActivity.k.getText().toString() + "``") + inputActivity.l.getText().toString() + "``") + inputActivity.m.getText().toString() + "``") + inputActivity.n.getText().toString() + "``");
                    applicationContext = inputActivity.getApplicationContext();
                    str = "File Saved!..";
                }
                Toast.makeText(applicationContext, str, 0).show();
            }
        });
    }

    @Override // android.app.Activity
    protected Dialog onCreateDialog(int i) {
        if (i != 0) {
            if (i != 999) {
                return null;
            }
            return new TimePickerDialog(this, this.H, this.B, this.C, false);
        }
        return new DatePickerDialog(this, this.G, this.y, this.z, this.A);
    }
}
