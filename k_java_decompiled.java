package enc.icssoftwares.com.vakkiampro;

import android.content.Context;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
/* loaded from: classes.dex */
public final class k {
    private long B;
    private long C;
    private long D;
    private long E;
    private long F;
    private long G;
    private long H;
    private long I;

    /* renamed from: a  reason: collision with root package name */
    public int f694a;
    public int c;
    public int d;
    public int e;
    public int f;
    public int g;
    Context w;
    private String y = "";
    private int[] z = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    private Date[] A = {new Date(), new Date(), new Date(), new Date(), new Date(), new Date(), new Date(), new Date(), new Date(), new Date(), new Date(), new Date(), new Date(), new Date(), new Date()};
    public String b = "";
    String x = "";
    f h = new f();
    f i = new f();
    f j = new f();
    g l = new g();
    f k = new f();
    d m = new d();
    e n = new e();
    s o = new s();
    s p = new s();
    s q = new s();
    s r = new s();
    s s = new s();
    s t = new s();
    s u = new s();
    s v = new s();

    /* JADX INFO: Access modifiers changed from: package-private */
    public k(Context context) {
        this.w = context;
    }

    private static int a(Date date, Date date2) {
        return (int) ((date.getTime() - date2.getTime()) / 86400000);
    }

    private static String a(Context context, long j) {
        StringBuilder sb;
        int i;
        new h();
        if (j <= 468) {
            sb = new StringBuilder();
            i = C0023R.raw.arp;
        } else {
            sb = new StringBuilder();
            i = C0023R.raw.pys;
        }
        sb.append(h.a(context, i, "R".concat(String.valueOf(j))));
        sb.append("=");
        return sb.toString().split("=")[1].toString();
    }

    private Date a(int i, int i2, int i3) {
        new Date();
        a(i - 3101);
        Date a2 = a(this.A[0], i3);
        for (int i4 = 1; i4 <= i2; i4++) {
            a2 = a(a2, this.z[i4 - 1]);
        }
        return a(a2, -1);
    }

    private static Date a(Date date, int i) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        calendar.add(5, i);
        return calendar.getTime();
    }

    private void a(int i) {
        s[] sVarArr = {new s(), new s(), new s(), new s(), new s(), new s(), new s(), new s(), new s(), new s(), new s(), new s(), new s()};
        sVarArr[0].f704a = 0;
        sVarArr[0].b = 0;
        sVarArr[0].c = 0;
        sVarArr[0].d = 0;
        sVarArr[1].f704a = 30;
        sVarArr[1].b = 55;
        sVarArr[1].c = 32;
        sVarArr[1].d = 0;
        sVarArr[2].f704a = 62;
        sVarArr[2].b = 19;
        sVarArr[2].c = 44;
        sVarArr[2].d = 0;
        sVarArr[3].f704a = 93;
        sVarArr[3].b = 56;
        sVarArr[3].c = 22;
        sVarArr[3].d = 0;
        sVarArr[4].f704a = 125;
        sVarArr[4].b = 24;
        sVarArr[4].c = 34;
        sVarArr[4].d = 0;
        sVarArr[5].f704a = 156;
        sVarArr[5].b = 26;
        sVarArr[5].c = 44;
        sVarArr[5].d = 0;
        sVarArr[6].f704a = 186;
        sVarArr[6].b = 54;
        sVarArr[6].c = 6;
        sVarArr[6].d = 0;
        sVarArr[7].f704a = 216;
        sVarArr[7].b = 48;
        sVarArr[7].c = 13;
        sVarArr[7].d = 0;
        sVarArr[8].f704a = 246;
        sVarArr[8].b = 18;
        sVarArr[8].c = 37;
        sVarArr[8].d = 0;
        sVarArr[9].f704a = 275;
        sVarArr[9].b = 39;
        sVarArr[9].c = 30;
        sVarArr[9].d = 0;
        sVarArr[10].f704a = 305;
        sVarArr[10].b = 6;
        sVarArr[10].c = 46;
        sVarArr[10].d = 0;
        sVarArr[11].f704a = 334;
        sVarArr[11].b = 55;
        sVarArr[11].c = 10;
        sVarArr[11].d = 0;
        sVarArr[12].f704a = 365;
        sVarArr[12].b = 15;
        sVarArr[12].c = 31;
        sVarArr[12].d = 15;
        int i2 = i - 1;
        this.d = sVarArr[i2].f704a;
        this.e = sVarArr[i2].b;
        this.f = sVarArr[i2].c;
        this.g = sVarArr[i2].d;
    }

    /* JADX WARN: Removed duplicated region for block: B:27:0x0113  */
    /* JADX WARN: Removed duplicated region for block: B:28:0x0118  */
    /* JADX WARN: Removed duplicated region for block: B:31:0x03ef  */
    /*
        Code decompiled incorrectly, please refer to instructions dump.
        To view partially-correct add '--show-bad-code' argument
    */
    private void a(long r27) {
        /*
            Method dump skipped, instructions count: 1138
            To view this dump add '--comments-level debug' option
        */
        throw new UnsupportedOperationException("Method not decompiled: enc.icssoftwares.com.vakkiampro.k.a(long):void");
    }

    private static boolean a(long j, Date date) {
        String str = "";
        switch ((int) j) {
            case 0:
            case 7:
            case 14:
                str = "FRIDAY";
                break;
            case 1:
            case 8:
                str = "SATURDAY";
                break;
            case 2:
            case 9:
                str = "SUNDAY";
                break;
            case 3:
            case 10:
                str = "MONDAY";
                break;
            case 4:
            case 11:
                str = "TUESDAY";
                break;
            case 5:
            case 12:
                str = "WEDNESDAY";
                break;
            case 6:
            case 13:
                str = "THURSDAY";
                break;
        }
        return j(date).toLowerCase().trim().equals(str.toLowerCase().trim());
    }

    private static String b(Context context, long j) {
        StringBuilder sb;
        int i;
        new h();
        if (j <= 168) {
            sb = new StringBuilder();
            i = C0023R.raw.boi;
        } else {
            sb = new StringBuilder();
            i = C0023R.raw.cip;
        }
        sb.append(h.a(context, i, "R".concat(String.valueOf(j))));
        sb.append("=");
        return sb.toString().split("=")[1].toString();
    }

    private static String c(Context context, long j) {
        StringBuilder sb;
        int i;
        new h();
        if (j <= 63) {
            sb = new StringBuilder();
            i = C0023R.raw.goa;
        } else {
            sb = new StringBuilder();
            i = C0023R.raw.dlf;
        }
        sb.append(h.a(context, i, "R".concat(String.valueOf(j))));
        sb.append("=");
        return sb.toString().split("=")[1].toString();
    }

    private static String d(Context context, long j) {
        StringBuilder sb;
        int i;
        new h();
        if (j <= 190) {
            sb = new StringBuilder();
            i = C0023R.raw.tcm;
        } else {
            sb = new StringBuilder();
            i = C0023R.raw.htc;
        }
        sb.append(h.a(context, i, "R".concat(String.valueOf(j))));
        sb.append("=");
        return sb.toString().split("=")[1].toString();
    }

    private static String e(Context context, long j) {
        StringBuilder sb;
        int i;
        new h();
        if (j <= 223) {
            sb = new StringBuilder();
            i = C0023R.raw.rap;
        } else {
            sb = new StringBuilder();
            i = C0023R.raw.qnl;
        }
        sb.append(h.a(context, i, "R".concat(String.valueOf(j))));
        sb.append("=");
        return sb.toString().split("=")[1].toString();
    }

    private void i(Date date) {
        new String[]{"", "", "", "", "", "", "", "", "", "", "", "", "", ""};
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(date);
        int i = calendar.get(1);
        calendar.get(2);
        calendar.get(5);
        long j = i;
        a(j);
        int a2 = a(date, this.A[0]);
        if (a2 < 0) {
            a(j - 1);
            a2 = a(date, this.A[0]);
        }
        int i2 = 0;
        while (i2 <= 11) {
            int[] iArr = this.z;
            if (a2 - iArr[i2] < 0) {
                break;
            }
            a2 -= iArr[i2];
            i2++;
        }
        if (i2 > 11 && a2 == 0) {
            i2 = 0;
            a2 = 0;
        }
        this.f694a = a2 + 1;
        StringBuilder sb = new StringBuilder("TamilMonth");
        int i3 = i2 + 1;
        sb.append(i3);
        this.b = sb.toString();
        this.c = i3;
    }

    private static String j(Date date) {
        try {
            return new SimpleDateFormat("EEEE").format(date);
        } catch (Exception e) {
            e.printStackTrace();
            return "";
        }
    }

    public final String a(Date date) {
        long j;
        boolean z;
        long j2;
        long j3;
        long j4;
        i(date);
        int i = this.c;
        int i2 = this.f694a;
        long[] jArr = {0, 0, 0, 0, 0, 0, 0, 0};
        int[] iArr = {0, 0, 0, 0, 0, 0, 0, 0};
        int[] iArr2 = {0, 0, 0, 0, 0, 0, 0, 0};
        int[] iArr3 = {0, 0, 0, 0, 0, 0, 0, 0};
        iArr3[0] = -402;
        iArr3[1] = 5;
        iArr3[2] = 27;
        iArr3[3] = 133;
        iArr3[4] = -504;
        iArr3[5] = 638;
        jArr[0] = 1552827;
        jArr[1] = 634089;
        jArr[2] = 132589;
        jArr[3] = 28857;
        jArr[4] = 17158;
        jArr[5] = 11699;
        iArr[0] = 35;
        iArr[1] = 9;
        iArr[2] = 21;
        iArr[3] = 41;
        iArr[4] = 37;
        iArr[5] = 4;
        iArr2[0] = 0;
        iArr2[1] = 0;
        iArr2[2] = 0;
        iArr2[3] = 0;
        iArr2[4] = 0;
        iArr2[5] = 0;
        a(i);
        long j5 = ((this.C + this.d) + i2) - 1;
        long j6 = this.D + this.e;
        long j7 = this.E + this.f;
        if (this.F + this.g > 29.0d) {
            j = 1;
            j7++;
        } else {
            j = 1;
        }
        if (j7 >= 60) {
            j7 -= 60;
            j6 += j;
        }
        if (j6 >= 60) {
            j6 -= 60;
            j5 += j;
        }
        long j8 = j6;
        long j9 = j7;
        int i3 = 0;
        int i4 = 0;
        while (i3 <= 5) {
            while (true) {
                if (j5 - jArr[i3] < 0) {
                    j4 = j6;
                    break;
                }
                j4 = j6;
                j9 -= iArr2[i3];
                if (j9 < 0) {
                    j9 += 60;
                    j8--;
                }
                j8 -= iArr[i3];
                int i5 = (j8 > 0L ? 1 : (j8 == 0L ? 0 : -1));
                if (i5 < 0 && j5 <= 0) {
                    j8 += iArr[i3];
                    break;
                }
                if (i5 < 0 && j5 > 0) {
                    j8 += 60;
                    j5--;
                }
                j5 -= jArr[i3];
                i4 += iArr3[i3];
                j6 = j4;
            }
            i3++;
            j6 = j4;
        }
        long j10 = j6;
        if (j5 < 0) {
            j5 = 0;
        }
        long j11 = 780;
        long j12 = j5 % 780;
        this.G = j12;
        int i6 = 1;
        while (i6 <= 39) {
            int i7 = (int) (j5 / j11);
            this.I = (i7 * 39) + i6;
            this.x = a(this.w, this.I);
            this.h.a(this.x);
            if (this.h.f689a == i7 + 1 && this.h.b > this.G) {
                break;
            }
            i6++;
            j11 = 780;
        }
        if (j5 == 0) {
            f fVar = this.h;
            fVar.c = 118L;
            fVar.d = 0L;
            fVar.e = -6L;
        }
        long j13 = this.h.c;
        long j14 = this.h.d;
        long j15 = this.h.e;
        long j16 = this.h.b;
        long j17 = j7;
        this.x = a(this.w, this.I - 1);
        this.h.a(this.x);
        long j18 = this.h.c;
        long j19 = this.h.d;
        long j20 = this.h.e;
        long j21 = this.h.b;
        long j22 = i4;
        long j23 = j20 * j22;
        long j24 = j22 * j15;
        long j25 = i4 * 60;
        long j26 = j23 + j25 + (((j18 * 60) + j19) * 60);
        long j27 = j25 + j24 + (((j13 * 60) + j14) * 60);
        if (j26 < 0) {
            j26 += 1296000;
            z = true;
        } else {
            z = false;
        }
        if (j27 < 0) {
            j27 += 1296000;
        }
        long abs = Math.abs(j27) - Math.abs(j26);
        s sVar = this.q;
        sVar.e = false;
        if (j26 > j27) {
            sVar.e = true;
            if (z) {
                sVar.e = false;
            }
            if (Math.abs(Math.abs(j27) - Math.abs(j26)) > 1080000) {
                j27 = Math.abs(j27) + 1296000;
                abs = Math.abs(j27) - Math.abs(j26);
                this.q.e = false;
            }
        }
        long abs2 = Math.abs(abs);
        long j28 = j12 - j21;
        long j29 = j16 - j21;
        long j30 = j9 - j17;
        if (j30 < 0) {
            j2 = 60;
            j30 += 60;
            j3 = 1;
            j8--;
        } else {
            j2 = 60;
            j3 = 1;
        }
        long j31 = j8 - j10;
        if (j31 < 0) {
            j31 += j2;
            j28 -= j3;
        }
        long j32 = j28 - 0;
        if (j10 >= 30) {
            j32 += j3;
        }
        Long.signum(j32);
        double d = (abs2 / ((j29 * 60) * 60)) * ((((j32 * 60) + j31) * 60) + j30);
        long j33 = (long) (j26 <= j27 ? d + j26 : j26 - d);
        long j34 = j33 % 60;
        long j35 = (int) (j33 / 60);
        long j36 = j35 % 60;
        long j37 = (int) (j35 / 60);
        while (j37 >= 360) {
            j37 -= 360;
        }
        s sVar2 = this.q;
        sVar2.f704a = (int) j37;
        sVar2.b = (int) j36;
        sVar2.c = (int) j34;
        sVar2.d = 0;
        return "Mars-" + this.q.f704a + "-" + this.q.b + "-" + this.q.c;
    }

    public final String b(Date date) {
        long j;
        long abs;
        boolean z;
        long j2;
        long j3;
        double d;
        s sVar;
        boolean z2;
        i(date);
        int i = this.c;
        int i2 = this.f694a;
        long[] jArr = {0, 0, 0, 0, 0, 0, 0, 0};
        int[] iArr = {0, 0, 0, 0, 0, 0, 0, 0};
        int[] iArr2 = {0, 0, 0, 0, 0, 0, 0, 0};
        int[] iArr3 = {0, 0, 0, 0, 0, 0, 0, 0};
        iArr3[0] = -261;
        iArr3[1] = 1;
        iArr3[2] = -9;
        iArr3[3] = 133;
        iArr3[4] = -71;
        iArr3[5] = -619;
        int i3 = 6;
        iArr3[6] = 274;
        jArr[0] = 1570425;
        jArr[1] = 974875;
        jArr[2] = 125648;
        jArr[3] = 65018;
        jArr[4] = 30315;
        jArr[5] = 21539;
        jArr[6] = 4387;
        iArr[0] = 17;
        iArr[1] = 26;
        iArr[2] = 50;
        iArr[3] = 17;
        iArr[4] = 17;
        iArr[5] = 48;
        iArr[6] = 44;
        iArr2[0] = 0;
        iArr2[1] = 0;
        iArr2[2] = 0;
        iArr2[3] = 0;
        iArr2[4] = 0;
        iArr2[5] = 0;
        iArr2[6] = 0;
        a(i);
        long j4 = this.D + this.e;
        long j5 = ((this.C + this.d) + i2) - 1;
        long j6 = this.E + this.f;
        if (this.F + this.g > 29.0d) {
            j6++;
        }
        if (j6 >= 60) {
            j6 -= 60;
            j4++;
        }
        if (j4 >= 60) {
            j4 -= 60;
            j5++;
        }
        long j7 = j4;
        long j8 = j6;
        int i4 = 0;
        int i5 = 0;
        while (true) {
            j = 0;
            if (i4 > i3) {
                break;
            }
            while (true) {
                if (j5 - jArr[i4] >= 0) {
                    j8 -= iArr2[i4];
                    if (j8 < 0) {
                        j8 += 60;
                        j7--;
                    }
                    j7 -= iArr[i4];
                    int i6 = (j7 > 0L ? 1 : (j7 == 0L ? 0 : -1));
                    if (i6 < 0 && j5 <= 0) {
                        j7 += iArr[i4];
                        break;
                    }
                    if (i6 < 0 && j5 > 0) {
                        j7 += 60;
                        j5--;
                    }
                    j5 -= jArr[i4];
                    i5 += iArr3[i4];
                }
            }
            i4++;
            i3 = 6;
        }
        if (j5 < 0) {
            j5 = 0;
        }
        long j9 = 399;
        long j10 = j5 % 399;
        this.G = j10;
        int i7 = 1;
        while (true) {
            if (i7 > 22) {
                break;
            }
            int i8 = (int) (j5 / j9);
            this.I = (i8 * 22) + i7;
            this.x = b(this.w, this.I);
            this.j.a(this.x);
            if (this.j.f689a == i8 + 1 && this.j.b > this.G) {
                j = 0;
                break;
            }
            i7++;
            j = 0;
            j9 = 399;
        }
        if (j5 == j) {
            f fVar = this.j;
            fVar.c = 180L;
            fVar.d = j;
            fVar.e = -4L;
        }
        long j11 = this.j.c;
        long j12 = this.j.d;
        long j13 = this.j.e;
        long j14 = j4;
        long j15 = this.j.b;
        long j16 = j6;
        this.x = b(this.w, this.I - 1);
        this.j.a(this.x);
        long j17 = this.j.c;
        long j18 = this.j.d;
        long j19 = this.j.e;
        long j20 = this.j.b;
        if (j17 < j11 && j11 - j17 > 300) {
            j17 += 360;
        }
        if (j17 > j11 && j17 - j11 > 300) {
            j11 += 360;
        }
        long j21 = i5;
        long j22 = j19 * j21;
        long j23 = j21 * j13;
        long j24 = i5 * 60;
        long j25 = j22 + j24 + (((j17 * 60) + j18) * 60);
        long j26 = j24 + j23 + (((j11 * 60) + j12) * 60);
        if (j25 < 0 || j26 < 0) {
            j25 += 1296000;
            j26 += 1296000;
        }
        Math.abs(j26);
        Math.abs(j25);
        if (Math.abs(j26) - Math.abs(j25) > 1080000) {
            abs = (j25 + 1296000) - j26;
            z = true;
        } else {
            abs = Math.abs(j26 - j25);
            z = false;
        }
        long abs2 = Math.abs(abs);
        long j27 = j10 - j20;
        long j28 = j15 - j20;
        long j29 = j8 - j16;
        if (j29 < 0) {
            j3 = 60;
            j29 += 60;
            j2 = 1;
            j7--;
        } else {
            j2 = 1;
            j3 = 60;
        }
        long j30 = j7 - j14;
        if (j30 < 0) {
            j30 += j3;
            j27 -= j2;
        }
        long j31 = j27 - 0;
        if (j14 >= 30) {
            j31 += j2;
        }
        Long.signum(j31);
        double d2 = (abs2 / ((j28 * 60) * 60)) * ((((j31 * 60) + j30) * 60) + j29);
        if (z) {
            j25 += 1296000;
        }
        if (j25 <= j26) {
            d = d2 + j25;
            sVar = this.s;
            z2 = false;
        } else {
            d = j25 - d2;
            sVar = this.s;
            z2 = true;
        }
        sVar.e = z2;
        long j32 = (long) d;
        long j33 = j32 % 60;
        long j34 = (int) (j32 / 60);
        long j35 = j34 % 60;
        long j36 = (int) (j34 / 60);
        while (j36 >= 360) {
            j36 -= 360;
        }
        s sVar2 = this.s;
        sVar2.f704a = (int) j36;
        sVar2.b = (int) j35;
        sVar2.c = (int) j33;
        sVar2.d = 0;
        return "Jupiter-" + this.s.f704a + "-" + this.s.b + "-" + this.s.c;
    }

    public final String c(Date date) {
        long j;
        long abs;
        boolean z;
        long j2;
        long j3;
        double d;
        s sVar;
        boolean z2;
        i(date);
        int i = this.c;
        int i2 = this.f694a;
        long[] jArr = {0, 0, 0, 0, 0, 0, 0, 0};
        int[] iArr = {0, 0, 0, 0, 0, 0, 0, 0};
        int[] iArr2 = {0, 0, 0, 0, 0, 0, 0, 0};
        int[] iArr3 = {0, 0, 0, 0, 0, 0, 0, 0};
        iArr3[0] = 18;
        iArr3[1] = 0;
        iArr3[2] = 28;
        iArr3[3] = -57;
        iArr3[4] = 2102;
        iArr3[5] = -144;
        jArr[0] = 1561937;
        jArr[1] = 437945;
        jArr[2] = 174594;
        jArr[3] = 88756;
        jArr[4] = 44962;
        jArr[5] = 2919;
        iArr[0] = 44;
        iArr[1] = 0;
        iArr[2] = 7;
        iArr[3] = 53;
        iArr[4] = 22;
        iArr[5] = 38;
        iArr2[0] = 0;
        iArr2[1] = 0;
        iArr2[2] = 0;
        iArr2[3] = 0;
        iArr2[4] = 0;
        iArr2[5] = 0;
        a(i);
        long j4 = ((this.C + this.d) + i2) - 1;
        long j5 = this.D + this.e;
        long j6 = this.E + this.f;
        if (this.F + this.g > 29.0d) {
            j6++;
        }
        if (j6 >= 60) {
            j6 -= 60;
            j5++;
        }
        if (j5 >= 60) {
            j5 -= 60;
            j4++;
        }
        long j7 = j6;
        long j8 = j4;
        long j9 = j5;
        int i3 = 0;
        int i4 = 0;
        while (true) {
            j = 0;
            if (i3 > 5) {
                break;
            }
            while (true) {
                if (j8 - jArr[i3] >= 0) {
                    j7 -= iArr2[i3];
                    if (j7 < 0) {
                        j7 += 60;
                        j9--;
                    }
                    j9 -= iArr[i3];
                    int i5 = (j9 > 0L ? 1 : (j9 == 0L ? 0 : -1));
                    if (i5 < 0 && j8 <= 0) {
                        j9 += iArr[i3];
                        break;
                    }
                    if (i5 < 0 && j8 > 0) {
                        j9 += 60;
                        j8--;
                    }
                    j8 -= jArr[i3];
                    i4 += iArr3[i3];
                }
            }
            i3++;
        }
        if (j8 < 0) {
            j8 = 0;
        }
        long j10 = 584;
        long j11 = j8 % 584;
        this.G = j11;
        int i6 = 1;
        while (true) {
            if (i6 > 40) {
                break;
            }
            int i7 = (int) (j8 / j10);
            this.I = (i7 * 40) + i6;
            this.x = c(this.w, this.I);
            this.l.a(this.x);
            if (this.l.f690a == i7 + 1 && this.l.b > this.G) {
                j = 0;
                break;
            }
            i6++;
            j = 0;
            j10 = 584;
        }
        if (j8 == j) {
            g gVar = this.l;
            gVar.c = 93L;
            gVar.d = j;
            gVar.e = -1.0d;
        }
        long j12 = this.l.c;
        long j13 = this.l.d;
        double d2 = this.l.f;
        long j14 = this.l.b;
        long j15 = j6;
        this.x = c(this.w, this.I - 1);
        this.l.a(this.x);
        long j16 = this.l.c;
        long j17 = this.l.d;
        double d3 = this.l.f;
        long j18 = this.l.b;
        if (j16 < j12 && j12 - j16 > 300) {
            j16 += 360;
        }
        if (j16 > j12 && j16 - j12 > 300) {
            j12 += 360;
        }
        double d4 = i4;
        long j19 = i4 * 60;
        long j20 = ((long) (d3 * d4)) + j19 + (((j16 * 60) + j17) * 60);
        long j21 = j19 + ((long) (d4 * d2)) + (((j12 * 60) + j13) * 60);
        if (j20 < 0 || j21 < 0) {
            j20 += 1296000;
            j21 += 1296000;
        }
        Math.abs(j21);
        Math.abs(j20);
        if (Math.abs(j21) - Math.abs(j20) > 1080000) {
            abs = (j20 + 1296000) - j21;
            z = true;
        } else {
            abs = Math.abs(j21 - j20);
            z = false;
        }
        long abs2 = Math.abs(abs);
        long j22 = j11 - j18;
        long j23 = j14 - j18;
        long j24 = j7 - j15;
        if (j24 < 0) {
            j3 = 60;
            j24 += 60;
            j2 = 1;
            j9--;
        } else {
            j2 = 1;
            j3 = 60;
        }
        long j25 = j9 - j5;
        if (j25 < 0) {
            j25 += j3;
            j22 -= j2;
        }
        long j26 = j22 - 0;
        if (j5 >= 30) {
            j26 += j2;
        }
        Long.signum(j26);
        double d5 = (abs2 / ((j23 * 60) * 60)) * ((((j26 * 60) + j25) * 60) + j24);
        if (z) {
            j20 += 1296000;
        }
        if (j20 <= j21) {
            d = d5 + j20;
            sVar = this.t;
            z2 = false;
        } else {
            d = j20 - d5;
            sVar = this.t;
            z2 = true;
        }
        sVar.e = z2;
        long j27 = (long) d;
        long j28 = j27 % 60;
        long j29 = (int) (j27 / 60);
        long j30 = j29 % 60;
        long j31 = (int) (j29 / 60);
        while (j31 >= 360) {
            j31 -= 360;
        }
        s sVar2 = this.t;
        sVar2.f704a = (int) j31;
        sVar2.b = (int) j30;
        sVar2.c = (int) j28;
        sVar2.d = 0;
        return "Venus-" + this.t.f704a + "-" + this.t.b + "-" + this.t.c;
    }

    public final String d(Date date) {
        long j;
        long j2;
        long abs;
        boolean z;
        long j3;
        long j4;
        double d;
        s sVar;
        boolean z2;
        i(date);
        int i = this.c;
        int i2 = this.f694a;
        long[] jArr = {0, 0, 0, 0, 0, 0, 0, 0};
        int[] iArr = {0, 0, 0, 0, 0, 0, 0, 0};
        int[] iArr2 = {0, 0, 0, 0, 0, 0, 0, 0};
        int[] iArr3 = {0, 0, 0, 0, 0, 0, 0, 0};
        iArr3[0] = -326;
        iArr3[1] = 5;
        iArr3[2] = -13;
        iArr3[3] = 43;
        iArr3[4] = 401;
        jArr[0] = 1589474;
        jArr[1] = 570534;
        jArr[2] = 182994;
        jArr[3] = 21551;
        jArr[4] = 10964;
        iArr[0] = 28;
        iArr[1] = 8;
        iArr[2] = 23;
        iArr[3] = 0;
        iArr[4] = 32;
        iArr2[0] = 0;
        iArr2[1] = 0;
        iArr2[2] = 0;
        iArr2[3] = 0;
        iArr2[4] = 0;
        a(i);
        long j5 = ((this.C + this.d) + i2) - 1;
        System.out.println("Yv=".concat(String.valueOf(j5)));
        long j6 = this.D + this.e;
        long j7 = this.E + this.f;
        if (this.F + this.g > 29.0d) {
            j = 1;
            j7++;
        } else {
            j = 1;
        }
        if (j7 >= 60) {
            j7 -= 60;
            j6 += j;
        }
        if (j6 >= 60) {
            j6 -= 60;
            j5 += j;
        }
        long j8 = j7;
        long j9 = j6;
        int i3 = 0;
        for (int i4 = 0; i4 <= 4; i4++) {
            System.out.print("\nNow I is=".concat(String.valueOf(i4)));
            while (true) {
                if (j5 - jArr[i4] > 0) {
                    j8 -= iArr2[i4];
                    if (j8 < 0) {
                        j8 += 60;
                        j9--;
                    }
                    long j10 = j9 - iArr[i4];
                    int i5 = (j10 > 0L ? 1 : (j10 == 0L ? 0 : -1));
                    if (i5 < 0 && j5 <= 0) {
                        j9 = j10 + iArr[i4];
                        break;
                    }
                    if (i5 < 0 && j5 > 0) {
                        j10 += 60;
                        j5--;
                    }
                    j5 -= jArr[i4];
                    System.out.println("\nNow Yv=" + j5 + " MandDays=" + jArr[i4]);
                    i3 += iArr3[i4];
                    j9 = j10;
                }
            }
        }
        if (j5 < 0) {
            j5 = 0;
        }
        this.G = j5;
        while (true) {
            long j11 = this.G;
            j2 = 378;
            if (j11 < 378) {
                break;
            }
            this.G = j11 - 378;
        }
        int i6 = 1;
        while (i6 <= 29) {
            int i7 = (int) (j5 / j2);
            this.I = (i7 * 20) + i6;
            System.out.println("Saturn RecNo1=" + this.I + " " + j5 + " 378 " + this.G);
            long j12 = this.I;
            if (j12 > 580) {
                this.I = j12 - 578;
            }
            System.out.println("Saturn RecNo2=" + this.I);
            this.x = d(this.w, this.I);
            this.k.a(this.x);
            if (this.k.f689a == (i7 % 29) + 1 && this.k.b >= this.G) {
                break;
            }
            i6++;
            j2 = 378;
        }
        if (j5 == 0) {
            f fVar = this.k;
            fVar.c = 236L;
            fVar.d = 0L;
            fVar.e = -6L;
        }
        long j13 = this.k.c;
        long j14 = this.k.d;
        long j15 = this.k.e;
        long j16 = j9;
        long j17 = this.k.b;
        long j18 = j7;
        this.x = d(this.w, this.I - 1);
        this.k.a(this.x);
        long j19 = this.k.c;
        long j20 = this.k.d;
        long j21 = j5;
        long j22 = this.k.e;
        long j23 = this.k.b;
        if (j19 < j13 && j13 - j19 > 300) {
            j19 += 360;
        }
        if (j19 > j13 && j19 - j13 > 300) {
            j13 += 360;
        }
        int i8 = i3 * 60;
        long j24 = i3;
        long j25 = j22 * j24;
        long j26 = j24 * j15;
        long j27 = i8;
        long j28 = j25 + j27 + (((j19 * 60) + j20) * 60);
        long j29 = j27 + j26 + (((j13 * 60) + j14) * 60);
        if (j28 < 0 || j29 < 0) {
            j28 += 1296000;
            j29 += 1296000;
        }
        Math.abs(j29);
        Math.abs(j28);
        if (Math.abs(j29) - Math.abs(j28) > 1080000) {
            abs = (j28 + 1296000) - j29;
            z = true;
        } else {
            abs = Math.abs(j29 - j28);
            z = false;
        }
        long abs2 = Math.abs(abs);
        long j30 = (j21 % 378) - j23;
        long j31 = j17 - j23;
        long j32 = j8 - j18;
        if (j32 < 0) {
            j4 = 60;
            j32 += 60;
            j3 = 1;
            j16--;
        } else {
            j3 = 1;
            j4 = 60;
        }
        long j33 = j16 - j6;
        if (j33 < 0) {
            j33 += j4;
            j30 -= j3;
        }
        long j34 = j30 - 0;
        if (j6 >= 30) {
            j34 += j3;
        }
        Long.signum(j34);
        double d2 = (abs2 / ((j31 * 60) * 60)) * ((((j34 * 60) + j33) * 60) + j32);
        if (z) {
            j28 += 1296000;
        }
        if (j28 <= j29) {
            d = d2 + j28;
            sVar = this.u;
            z2 = false;
        } else {
            d = j28 - d2;
            sVar = this.u;
            z2 = true;
        }
        sVar.e = z2;
        long j35 = (long) d;
        long j36 = j35 % 60;
        long j37 = (int) (j35 / 60);
        long j38 = j37 % 60;
        long j39 = (int) (j37 / 60);
        while (j39 >= 360) {
            j39 -= 360;
        }
        s sVar2 = this.u;
        sVar2.f704a = (int) j39;
        sVar2.b = (int) j38;
        sVar2.c = (int) j36;
        sVar2.d = 0;
        return "Saturn-" + this.u.f704a + "-" + this.u.b + "-" + this.u.c;
    }

    public final String e(Date date) {
        double d;
        i(date);
        int i = this.c;
        int i2 = this.f694a;
        double[] dArr = {0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d};
        double[] dArr2 = {0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d};
        dArr[0] = 12000.0d;
        dArr[1] = 6000.0d;
        dArr[2] = 3000.0d;
        dArr[3] = 1500.0d;
        dArr[4] = 750.0d;
        dArr[5] = 375.0d;
        dArr[6] = 187.5d;
        dArr[7] = 93.75d;
        dArr[8] = 46.88d;
        dArr[9] = 23.44d;
        dArr[10] = 11.72d;
        dArr[11] = 5.86d;
        dArr[12] = 2.93d;
        dArr[13] = 1.46d;
        dArr[14] = 0.73d;
        dArr[15] = 0.37d;
        dArr[16] = 0.18d;
        dArr2[0] = 225632.0d;
        dArr2[1] = 112816.0d;
        dArr2[2] = 56408.0d;
        dArr2[3] = 28204.0d;
        dArr2[4] = 14102.0d;
        dArr2[5] = 7051.0d;
        dArr2[6] = 3525.5d;
        dArr2[7] = 1762.75d;
        dArr2[8] = 881.38d;
        dArr2[9] = 440.69d;
        dArr2[10] = 220.34d;
        dArr2[11] = 110.17d;
        dArr2[12] = 55.09d;
        dArr2[13] = 27.54d;
        dArr2[14] = 13.77d;
        dArr2[15] = 6.89d;
        dArr2[16] = 3.44d;
        a(i);
        long j = ((this.C + this.d) + i2) - 1;
        long j2 = this.D + this.e;
        long j3 = this.E + this.f;
        if (this.F + this.g > 29.0d) {
            j3++;
        }
        if (j3 >= 60) {
            j3 -= 60;
            j2++;
        }
        if (j2 >= 60) {
            j2 -= 60;
            j++;
        }
        long j4 = j - 1600066;
        long j5 = j4 % 6792;
        long j6 = (j5 % 566) * 30;
        long j7 = ((int) (j6 / 566)) + (((int) (j5 / 566)) * 30);
        long j8 = (j6 % 566) * 60;
        long j9 = (int) (j8 / 566);
        long j10 = (int) (((j8 % 566) * 60) / 566);
        long j11 = (int) (j4 / 5654);
        long j12 = (int) (((j4 % 5654) * 30) / 5654);
        while (j12 >= 60) {
            j11++;
            j12 -= 60;
        }
        long j13 = 0;
        while (j11 >= 60) {
            j13++;
            j11 -= 60;
        }
        long j14 = j10 - j12;
        if (j14 < 0) {
            j14 += 60;
            j9--;
        }
        long j15 = j9 - j11;
        if (j15 < 0) {
            j15 += 60;
            j7--;
        }
        long j16 = j7 - j13;
        if (j16 < 0) {
            j16 += 360;
        }
        Long.signum(j2);
        double d2 = 0.0d;
        double d3 = (j2 * 60) + j3;
        for (int i3 = 0; i3 <= 16; i3++) {
            while (d3 >= dArr2[i3]) {
                d3 -= dArr2[i3];
                d2 += dArr[i3];
            }
        }
        double d4 = (1296000.0d - (((((j16 * 60) + j15) * 60) + j14) - d2)) - 300.0d;
        if (d4 < 0.0d) {
            d4 += 1296000.0d;
        }
        s sVar = this.v;
        sVar.f704a = (int) (d / 60.0d);
        sVar.b = (int) (((long) ((int) (d4 / 60.0d))) % 60);
        sVar.c = (int) (((long) d4) % 60);
        sVar.d = 0;
        sVar.e = true;
        return "Rahu-" + this.v.f704a + "-" + this.v.b + "-" + this.v.c;
    }

    /* JADX WARN: Code restructure failed: missing block: B:29:0x02a4, code lost:
        if (r14 > 248) goto L33;
     */
    /* JADX WARN: Code restructure failed: missing block: B:30:0x02a6, code lost:
        r32 = r32 + 99846;
        r14 = r14 - 248;
     */
    /* JADX WARN: Code restructure failed: missing block: B:31:0x02aa, code lost:
        r3 = r32;
     */
    /* JADX WARN: Code restructure failed: missing block: B:35:0x02b7, code lost:
        if (r14 > 248) goto L33;
     */
    /* JADX WARN: Removed duplicated region for block: B:40:0x02c0  */
    /* JADX WARN: Removed duplicated region for block: B:44:0x0451  */
    /* JADX WARN: Removed duplicated region for block: B:45:0x0456  */
    /* JADX WARN: Removed duplicated region for block: B:46:0x045b  */
    /* JADX WARN: Removed duplicated region for block: B:47:0x0460  */
    /* JADX WARN: Removed duplicated region for block: B:48:0x0465  */
    /* JADX WARN: Removed duplicated region for block: B:49:0x046a  */
    /* JADX WARN: Removed duplicated region for block: B:50:0x046f  */
    /* JADX WARN: Removed duplicated region for block: B:51:0x0474  */
    /* JADX WARN: Removed duplicated region for block: B:52:0x0479  */
    /* JADX WARN: Removed duplicated region for block: B:53:0x047e  */
    /* JADX WARN: Removed duplicated region for block: B:54:0x0483  */
    /* JADX WARN: Removed duplicated region for block: B:55:0x0488  */
    /* JADX WARN: Removed duplicated region for block: B:57:0x048e A[PHI: r28 
      PHI: (r28v1 long) = (r28v0 long), (r28v3 long) binds: [B:42:0x044d, B:56:0x048c] A[DONT_GENERATE, DONT_INLINE]] */
    /* JADX WARN: Removed duplicated region for block: B:60:0x04b3 A[LOOP:1: B:58:0x04ad->B:60:0x04b3, LOOP_END] */
    /*
        Code decompiled incorrectly, please refer to instructions dump.
        To view partially-correct add '--show-bad-code' argument
    */
    public final java.lang.String f(java.util.Date r41) {
        /*
            Method dump skipped, instructions count: 1600
            To view this dump add '--comments-level debug' option
        */
        throw new UnsupportedOperationException("Method not decompiled: enc.icssoftwares.com.vakkiampro.k.f(java.util.Date):java.lang.String");
    }

    public final String g(Date date) {
        long j;
        long j2;
        long j3;
        long j4;
        long j5;
        long j6;
        long j7;
        int i;
        i(date);
        int i2 = this.c;
        int i3 = this.f694a;
        long[] jArr = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
        long[] jArr2 = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
        long[] jArr3 = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
        a(i2);
        long j8 = this.D;
        long j9 = this.E;
        if (i2 == 1) {
            a(13);
        }
        long j10 = 0;
        if ((j8 * 60) + j9 < 1856) {
            j = 15 - r10;
            j2 = 31 - j9;
            j3 = 15 - j8;
            j4 = 365;
        } else {
            j = 0 - r10;
            j2 = 0 - j9;
            j3 = 60 - j8;
            j4 = 0;
        }
        if (j < 0) {
            j += 60;
            j2--;
        }
        if (j2 < 0) {
            j2 += 60;
            j3--;
        }
        if (j3 < 0) {
            j3 += 60;
            j4--;
        }
        if (j4 < 0) {
            j4 += 360;
        }
        jArr2[0] = 0;
        jArr2[1] = 14;
        jArr2[2] = 32;
        jArr2[3] = 54;
        jArr2[4] = 78;
        jArr2[5] = 105;
        jArr2[6] = 133;
        jArr2[7] = 163;
        jArr2[8] = 194;
        jArr2[9] = 224;
        jArr2[10] = 254;
        jArr2[11] = 284;
        jArr2[12] = 311;
        jArr2[13] = 335;
        jArr2[14] = 358;
        jArr2[15] = 376;
        jArr2[16] = 391;
        jArr2[17] = 403;
        jArr2[18] = 411;
        jArr2[19] = 415;
        jArr2[20] = 416;
        jArr2[21] = 412;
        jArr2[22] = 406;
        jArr2[23] = 398;
        jArr2[24] = 386;
        jArr2[25] = 374;
        jArr2[26] = 361;
        jArr2[27] = 347;
        jArr2[28] = 334;
        jArr2[29] = 322;
        jArr2[30] = 311;
        jArr2[31] = 303;
        jArr2[32] = 297;
        jArr2[33] = 295;
        jArr2[34] = 296;
        jArr2[35] = 301;
        jArr2[36] = 309;
        jArr2[37] = 322;
        jArr[0] = 84;
        jArr[1] = 108;
        jArr[2] = 132;
        jArr[3] = 144;
        jArr[4] = 162;
        jArr[5] = 168;
        jArr[6] = 180;
        jArr[7] = 186;
        jArr[8] = 180;
        jArr[9] = 180;
        jArr[10] = 180;
        jArr[11] = 162;
        jArr[12] = 144;
        jArr[13] = 138;
        jArr[14] = 108;
        jArr[15] = 90;
        jArr[16] = 72;
        jArr[17] = 48;
        jArr[18] = 24;
        jArr[19] = 6;
        jArr[20] = -24;
        jArr[21] = -36;
        jArr[22] = -48;
        jArr[23] = -72;
        jArr[24] = -72;
        jArr[25] = -78;
        jArr[26] = -84;
        jArr[27] = -78;
        jArr[28] = -72;
        jArr[29] = -66;
        jArr[30] = -48;
        jArr[31] = -36;
        jArr[32] = -12;
        jArr[33] = 6;
        jArr[34] = 30;
        jArr[35] = 48;
        jArr[36] = 78;
        int i4 = (int) (j4 / 10);
        if (i4 > 37) {
            i4 = 0;
        }
        long j11 = jArr2[i4];
        if (i4 > 36) {
            i4 = 0;
        }
        char c = jArr[i4] > 0 ? (char) 1 : (char) 65535;
        double abs = (((Math.abs(j5) * 60) * (((((((j4 % 10) * 60) + j3) * 60) + j2) * 60) + j)) / 216) / 1000.0d;
        long j12 = j11 * 60 * 60;
        long j13 = (long) (c > 0 ? j12 + abs : j12 - abs);
        long j14 = j13 % 60;
        long j15 = (int) (j13 / 60);
        long j16 = j15 % 60;
        long j17 = j - j14;
        long j18 = j2 - j16;
        long j19 = j3 - (((int) (j15 / 60)) % 60);
        long j20 = j4 - ((int) (j6 / 60));
        if (j17 < 0) {
            j17 += 60;
            j18--;
        }
        if (j18 < 0) {
            j18 += 60;
            j19--;
        }
        if (j19 < 0) {
            j19 += 60;
            j20--;
        }
        if (j20 < 0) {
            j20 += 360;
        }
        jArr3[0] = 3516;
        jArr3[1] = 3492;
        jArr3[2] = 3468;
        jArr3[3] = 3456;
        jArr3[4] = 3438;
        jArr3[5] = 3432;
        jArr3[6] = 3420;
        jArr3[7] = 3414;
        jArr3[8] = 3420;
        jArr3[9] = 3420;
        jArr3[10] = 3420;
        jArr3[11] = 3438;
        jArr3[12] = 3456;
        jArr3[13] = 3462;
        jArr3[14] = 3492;
        jArr3[15] = 3510;
        jArr3[16] = 3528;
        jArr3[17] = 3552;
        jArr3[18] = 3576;
        jArr3[19] = 3594;
        jArr3[20] = 3624;
        jArr3[21] = 3636;
        jArr3[22] = 3648;
        jArr3[23] = 3672;
        jArr3[24] = 3672;
        jArr3[25] = 3678;
        jArr3[26] = 3684;
        jArr3[27] = 3678;
        jArr3[28] = 3672;
        jArr3[29] = 3666;
        jArr3[30] = 3648;
        jArr3[31] = 3636;
        jArr3[32] = 3612;
        jArr3[33] = 3594;
        jArr3[34] = 3570;
        jArr3[35] = 3552;
        jArr3[36] = 3522;
        if (i2 == 1) {
            j7 = i3;
        } else {
            for (int i5 = 0; i5 <= i2 - 2; i5++) {
                j10 += this.z[i5];
            }
            j7 = j10 + i3;
        }
        for (int i6 = 0; i6 <= j7 - 2; i6++) {
            j19 += (int) (jArr3[i] / 60);
            j18 += jArr3[(i6 + 2) / 10] % 60;
            if (j18 >= 60) {
                j19++;
                j18 -= 60;
            }
            if (j19 >= 60) {
                j20++;
                j19 -= 60;
            }
            if (j17 >= 60) {
                j17 -= 60;
                j18++;
            }
            if (j18 >= 60) {
                j19++;
                j18 -= 60;
            }
            if (j19 >= 60) {
                j20++;
                j19 -= 60;
            }
            if (j20 >= 360) {
                j20 -= 360;
            }
        }
        s sVar = this.o;
        sVar.f704a = (int) j20;
        sVar.b = (int) j19;
        sVar.c = (int) j18;
        return "Sun-" + j20 + "-" + j19 + "-" + j18;
    }

    public final String h(Date date) {
        long j;
        int i;
        boolean z;
        long j2;
        long j3;
        long j4;
        i(date);
        int i2 = this.c;
        int i3 = this.f694a;
        new Date();
        long[] jArr = {0, 0, 0, 0, 0, 0, 0, 0};
        int[] iArr = {0, 0, 0, 0, 0, 0, 0, 0};
        int[] iArr2 = {0, 0, 0, 0, 0, 0, 0, 0};
        int[] iArr3 = {0, 0, 0, 0, 0, 0, 0, 0};
        iArr3[0] = -33;
        iArr3[1] = -1;
        iArr3[2] = 149;
        iArr3[3] = -446;
        jArr[0] = 1592740;
        jArr[1] = 16801;
        jArr[2] = 4750;
        jArr[3] = 2549;
        iArr[0] = 22;
        iArr[1] = 54;
        iArr[2] = 53;
        iArr[3] = 15;
        iArr2[0] = 0;
        iArr2[1] = 0;
        iArr2[2] = 0;
        iArr2[3] = 0;
        a((int) this.B, i2 - 1, i3);
        a(i2);
        long j5 = ((this.C + this.d) + i3) - 1;
        long j6 = this.D + this.e;
        long j7 = this.E + this.f;
        if (this.F + this.g > 29.0d) {
            j = 1;
            j7++;
        } else {
            j = 1;
        }
        if (j7 >= 60) {
            j7 -= 60;
            j6 += j;
        }
        if (j6 >= 60) {
            j6 -= 60;
            j5 += j;
        }
        long j8 = j5;
        long j9 = j7;
        long j10 = j6;
        int i4 = 0;
        int i5 = 0;
        while (i4 <= 3) {
            while (true) {
                if (j8 - jArr[i4] < 0) {
                    j4 = j6;
                    break;
                }
                j4 = j6;
                j9 -= iArr2[i4];
                if (j9 < 0) {
                    j9 += 60;
                    j10--;
                }
                j10 -= iArr[i4];
                int i6 = (j10 > 0L ? 1 : (j10 == 0L ? 0 : -1));
                if (i6 < 0 && j8 <= 0) {
                    j10 += iArr[i4];
                    break;
                }
                if (i6 < 0 && j8 > 0) {
                    j10 += 60;
                    j8--;
                }
                j8 -= jArr[i4];
                i5 += iArr3[i4];
                j6 = j4;
            }
            i4++;
            j6 = j4;
        }
        long j11 = j6;
        if (j8 < 0) {
            j8 = 0;
        }
        long j12 = 116;
        long j13 = j8 % 116;
        this.G = j13;
        int i7 = 1;
        while (true) {
            if (i7 > 25) {
                i = i5;
                break;
            }
            int i8 = (int) (j8 / j12);
            this.I = (i8 * 25) + i7;
            this.x = e(this.w, this.I);
            this.i.a(this.x);
            i = i5;
            if (this.i.f689a == i8 + 1 && this.i.b > this.G) {
                break;
            }
            i7++;
            i5 = i;
            j12 = 116;
        }
        if (j8 == 0) {
            f fVar = this.i;
            fVar.c = 240L;
            fVar.d = 0L;
            fVar.e = -3L;
        }
        long j14 = this.i.c;
        long j15 = this.i.d;
        long j16 = this.i.e;
        long j17 = this.i.b;
        this.x = e(this.w, this.I - 1);
        this.i.a(this.x);
        long j18 = this.i.c;
        long j19 = j7;
        long j20 = this.i.d;
        long j21 = this.i.e;
        long j22 = this.i.b;
        if (j18 < j14 && j14 - j18 > 300) {
            j18 += 360;
        }
        if (j18 > j14 && j18 - j14 > 300) {
            j14 += 360;
        }
        long j23 = i;
        long j24 = j21 * j23;
        long j25 = j23 * j16;
        long j26 = i * 60;
        long j27 = j24 + j26 + (((j18 * 60) + j20) * 60);
        long j28 = j26 + j25 + (((j14 * 60) + j15) * 60);
        if (j27 < 0) {
            j27 += 1296000;
            z = true;
        } else {
            z = false;
        }
        if (j28 < 0) {
            j28 += 1296000;
        }
        long abs = Math.abs(j28) - Math.abs(j27);
        System.out.println("Diff in Total=".concat(String.valueOf(abs)));
        s sVar = this.r;
        sVar.e = false;
        if (j27 > j28) {
            sVar.e = true;
            if (z) {
                sVar.e = false;
            }
            if (Math.abs(Math.abs(j28) - Math.abs(j27)) > 1080000) {
                j28 = Math.abs(j28) + 1296000;
                abs = Math.abs(j28) - Math.abs(j27);
                this.r.e = false;
            }
        }
        long abs2 = Math.abs(abs);
        System.out.println("DiffIntotal Abs=".concat(String.valueOf(abs2)));
        System.out.println("Yv=".concat(String.valueOf(j13)));
        long j29 = j13 - j22;
        long j30 = j17 - j22;
        long j31 = j9 - j19;
        if (j31 < 0) {
            j2 = 60;
            j31 += 60;
            j3 = 1;
            j10--;
        } else {
            j2 = 60;
            j3 = 1;
        }
        long j32 = j10 - j11;
        if (j32 < 0) {
            j32 += j2;
            j29 -= j3;
        }
        long j33 = j29 - 0;
        if (j11 >= 30) {
            j33 += j3;
        }
        Long.signum(j33);
        long j34 = (((j33 * 60) + j32) * 60) + j31;
        System.out.println("ValTot=".concat(String.valueOf(j34)));
        long j35 = j30 * 60 * 60;
        double d = (abs2 / j35) * j34;
        System.out.println("Mercury Ans=" + d + " Dx1=" + j35 + " ValTot=" + j34 + " DiffInTotal=" + abs2);
        long j36 = (long) (j27 <= j28 ? d + j27 : j27 - d);
        long j37 = j36 % 60;
        long j38 = (int) (j36 / 60);
        long j39 = j38 % 60;
        long j40 = (int) (j38 / 60);
        while (j40 >= 360) {
            j40 -= 360;
        }
        s sVar2 = this.r;
        sVar2.f704a = (int) j40;
        sVar2.b = (int) j39;
        sVar2.c = (int) j37;
        sVar2.d = 0;
        return "Mercury-" + this.r.f704a + "-" + this.r.b + "-" + this.r.c;
    }
}
