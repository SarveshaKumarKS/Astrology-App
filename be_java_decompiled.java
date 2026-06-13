package enc.icssoftwares.com.vakkiampro;

import android.support.v7.a.a;
import enc.icssoftwares.com.vakkiampro.bd;
import java.lang.reflect.Array;
/* loaded from: classes.dex */
public final class be extends bd {
    static int b = 0;
    static int c = 1;
    static int d = 2;
    static int e = 3;
    static boolean f = true;
    static boolean g = false;
    static final int[] h = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 0, 0, 0, 0, 12, 13, 14, 15, 16, 17};
    static double j = 4.84813681109536E-6d;
    static double[] m = {-13.12045233711d, -0.00113821591258d, -9.646018347184E-6d, 31.46734198839d, 0.0476835758578d, -3.421689790404E-4d, -6.84707090541d, -0.005834100476561d, -2.905334122698E-4d, -5.663161722088d, 0.005722859298199d, -8.466472828815E-5d, -84.29817796435d, -207.2552484689d, 7.876842214863d, 1.836463749022d, -15.57471855361d, -20.06969124724d, 21.52670284757d, -6.179946916139d, -0.9070028191196d, -12.70848233038d, -2.145589319058d, 13.81936399935d, -1.999840061168d};
    double A;
    double B;
    double C;
    double D;
    double E;
    double F;
    double G;
    double H;
    double I;
    double J;
    double K;
    double L;
    private bd.e N;
    double n;
    double o;
    double[] p;
    double q;
    double r;
    double s;
    double t;
    double u;
    double v;
    double w;
    double x;
    double y;
    double z;
    private long M = 0;
    long i = 0;
    double[][] k = (double[][]) Array.newInstance(double.class, 9, 24);
    double[][] l = (double[][]) Array.newInstance(double.class, 9, 24);

    /* JADX WARN: Removed duplicated region for block: B:170:0x065d A[LOOP:12: B:169:0x065b->B:170:0x065d, LOOP_END] */
    /*
        Code decompiled incorrectly, please refer to instructions dump.
        To view partially-correct add '--show-bad-code' argument
    */
    private int a(double r63, int r65, long r66) {
        /*
            Method dump skipped, instructions count: 1711
            To view this dump add '--comments-level debug' option
        */
        throw new UnsupportedOperationException("Method not decompiled: enc.icssoftwares.com.vakkiampro.be.a(double, int, long):int");
    }

    private int a(double d2, int i, long j2, long j3, String str) {
        if (((int) j2) != 4) {
            return 0;
        }
        if (a(d2, i, f, null, null, str) == -1) {
            return -1;
        }
        return (i == 0 ? a(j3, str) : a(i, j3, str)) == -1 ? -1 : 0;
    }

    private int a(double d2, int i, boolean z, double[] dArr, double[] dArr2, String str) {
        bd.d dVar;
        int i2;
        double d3;
        double[] dArr3;
        int i3;
        int i4;
        double d4;
        double[] dArr4;
        double[] dArr5;
        String str2 = str;
        int[] iArr = {2, 2, 0, 1, 3, 4, 5, 6, 7, 8};
        double[] dArr6 = new double[3];
        double[] dArr7 = new double[3];
        double[] dArr8 = new double[6];
        double[] dArr9 = new double[6];
        int i5 = iArr[i];
        bd.d dVar2 = this.f675a.d[i];
        bd.d dVar3 = this.f675a.d[0];
        double d5 = this.f675a.h.c;
        double d6 = this.f675a.h.d;
        if (z) {
            dArr9 = dVar2.x;
            dArr8 = dVar3.x;
        }
        double[] dArr10 = dArr8;
        double[] dArr11 = dArr9;
        boolean z2 = z || i == 0 || dArr2 != null;
        if (d2 < 625000.2d || d2 > 2818000.8d) {
            str2 = (str2 == null || str2 == "") ? "" : "";
            String str3 = "jd " + d2 + " outside Moshier planet range 625000.5 .. 2818000.5 ";
            if (str2.length() + str3.length() < 256) {
                StringBuilder sb = new StringBuilder();
                sb.append(str2);
                sb.append(str3);
                return -1;
            }
            return -1;
        }
        if (z2) {
            i2 = i5;
            if (d2 == dVar3.v && dVar3.w == 4) {
                dArr5 = dVar3.x;
                dVar = dVar2;
                d3 = d5;
                dArr3 = dArr11;
                i3 = 0;
                i4 = 2;
                d4 = d6;
            } else {
                b(d2, iArr[0], dArr10);
                bc.b(dArr10, 0, dArr10, 0);
                double d7 = -d5;
                bc.a(dArr10, 0, dArr10, 0, d7, d6);
                a(d2, dArr10);
                if (z) {
                    dVar3.v = d2;
                    dVar3.y = -1L;
                    dVar3.w = 4L;
                }
                double d8 = d2 - 1.0E-4d;
                b(d8, iArr[0], dArr7);
                bc.b(dArr7, 0, dArr7, 0);
                dArr3 = dArr11;
                d4 = d6;
                dVar = dVar2;
                d3 = d5;
                i3 = 0;
                bc.a(dArr7, 0, dArr7, 0, d7, d4);
                a(d8, dArr7);
                i4 = 2;
                for (int i6 = 0; i6 <= 2; i6++) {
                    dArr6[i6] = (dArr10[i6] - dArr7[i6]) / 1.0E-4d;
                }
                for (int i7 = 0; i7 <= 2; i7++) {
                    dArr10[i7 + 3] = dArr6[i7];
                }
                dArr5 = dArr10;
            }
            if (dArr2 != null) {
                for (int i8 = 0; i8 <= 5; i8++) {
                    dArr2[i8] = dArr5[i8];
                }
            }
        } else {
            dVar = dVar2;
            i2 = i5;
            d3 = d5;
            dArr3 = dArr11;
            i3 = 0;
            i4 = 2;
            d4 = d6;
        }
        if (i != 0) {
            if (d2 == dVar.v && dVar.w == 4) {
                dArr4 = dVar.x;
            } else {
                int i9 = i2;
                double[] dArr12 = dArr3;
                b(d2, i9, dArr12);
                bc.b(dArr12, i3, dArr12, i3);
                double d9 = -d3;
                bc.a(dArr12, 0, dArr12, 0, d9, d4);
                if (z) {
                    dVar.v = d2;
                    dVar.y = -1L;
                    dVar.w = 4L;
                }
                b(d2 - 1.0E-4d, i9, dArr7);
                bc.b(dArr7, i3, dArr7, i3);
                bc.a(dArr7, 0, dArr7, 0, d9, d4);
                for (int i10 = 0; i10 <= i4; i10++) {
                    dArr6[i10] = (dArr12[i10] - dArr7[i10]) / 1.0E-4d;
                }
                for (int i11 = 0; i11 <= i4; i11++) {
                    dArr12[i11 + 3] = dArr6[i11];
                }
                dArr4 = dArr12;
            }
            if (dArr != null) {
                for (int i12 = 0; i12 <= 5; i12++) {
                    dArr[i12] = dArr4[i12];
                }
            }
        }
        return i3;
    }

    private int a(double d2, long j2, boolean z, double[] dArr) {
        double d3;
        double d4;
        double d5;
        double d6;
        int i;
        double[] dArr2 = new double[2];
        if (this.f675a.f682a) {
            double b2 = d2 - bc.b(d2);
            if (this.f675a.g.f676a == d2 && this.f675a.i.f678a == d2) {
                d3 = this.f675a.g.b;
                dArr2[1] = this.f675a.i.b[1];
                dArr2[0] = this.f675a.i.b[0];
            } else {
                d3 = bc.d(d2);
                if ((j2 & 64) == 0) {
                    bc.a(d2, dArr2);
                }
            }
            int i2 = ((64 & j2) > 0L ? 1 : ((64 & j2) == 0L ? 0 : -1));
            if (i2 != 0) {
                d5 = d3;
                d4 = 0.0d;
            } else {
                double d7 = d3 + dArr2[1];
                d4 = dArr2[0];
                d5 = d7;
            }
            double a2 = bc.a(b2, d5, d4) * 15.0d;
            double cos = Math.cos(this.f675a.l.b * 0.0174532925199433d);
            double sin = Math.sin(this.f675a.l.b * 0.0174532925199433d);
            double sqrt = 1.0d / Math.sqrt((cos * cos) + ((sin * 0.9933056200098587d) * sin));
            double d8 = 0.9933056200098587d * sqrt;
            double cos2 = Math.cos((this.f675a.l.f683a + a2) * 0.0174532925199433d);
            double sin2 = Math.sin((this.f675a.l.f683a + a2) * 0.0174532925199433d);
            double d9 = this.f675a.l.c;
            double d10 = ((sqrt * 6378137.0d) + d9) * cos;
            dArr[0] = cos2 * d10;
            dArr[1] = d10 * sin2;
            dArr[2] = ((d8 * 6378137.0d) + d9) * sin;
            bc.a(dArr, 0, dArr, 0);
            dArr[3] = 6.300387486748799d;
            dArr[5] = 0.0d;
            dArr[4] = 0.0d;
            bc.d(dArr, 0, dArr, 0);
            for (int i3 = 0; i3 <= 5; i3++) {
                dArr[i3] = dArr[i3] / 1.4959787066E11d;
            }
            if (i2 == 0) {
                d6 = b2;
                bc.a(dArr, 0, dArr, 0, -this.f675a.i.c, this.f675a.i.d);
                if ((j2 & 256) != 0) {
                    bc.a(dArr, 3, dArr, 3, -this.f675a.i.c, this.f675a.i.d);
                }
                i = 1;
                a(dArr, j2, true);
            } else {
                d6 = b2;
                i = 1;
            }
            bc.a(dArr, 0, d2, i);
            if ((j2 & 256) != 0) {
                a(dArr, 0, d2, 1);
            }
            if (z) {
                for (int i4 = 0; i4 <= 5; i4++) {
                    this.f675a.l.f[i4] = dArr[i4];
                }
                this.f675a.l.d = d2;
                this.f675a.l.e = d6;
            }
            return 0;
        }
        return -1;
    }

    private int a(double d2, boolean z, double[] dArr, String str) {
        double[] dArr2 = new double[6];
        double[] dArr3 = new double[6];
        double[] dArr4 = new double[6];
        bd.d dVar = this.f675a.d[1];
        if (z) {
            dArr4 = dVar.x;
        }
        if (d2 < 625000.3d || d2 > 2818000.7d) {
            String str2 = str == "" ? "" : str;
            String str3 = (((("jd " + d2) + " outside Moshier's Moon range ") + 625000.5d) + " .. ") + 2818000.5d;
            if (str2.length() + str3.length() < 256) {
                StringBuilder sb = new StringBuilder();
                sb.append(str2);
                sb.append(str3);
                return -1;
            }
            return -1;
        } else if (d2 == dVar.v && dVar.w == 4) {
            if (dArr != null) {
                for (int i = 0; i <= 5; i++) {
                    dArr[i] = dVar.x[i];
                }
            }
            return 0;
        } else {
            b(d2, dArr4);
            if (z) {
                dVar.v = d2;
                dVar.y = -1L;
                dVar.w = 4L;
            }
            c(d2, dArr4);
            double d3 = d2 + 5.0E-5d;
            b(d3, dArr2);
            c(d3, dArr2);
            double d4 = d2 - 5.0E-5d;
            b(d4, dArr3);
            c(d4, dArr3);
            for (int i2 = 0; i2 <= 2; i2++) {
                dArr4[i2 + 3] = (((((dArr2[i2] + dArr3[i2]) / 2.0d) - dArr4[i2]) * 2.0d) + ((dArr2[i2] - dArr3[i2]) / 2.0d)) / 5.0E-5d;
            }
            if (dArr != null) {
                for (int i3 = 0; i3 <= 5; i3++) {
                    dArr[i3] = dArr4[i3];
                }
            }
            return 0;
        }
    }

    private int a(double d2, double[] dArr, int i, String str) {
        this.v = (d2 - 2451545.0d) / 36525.0d;
        double d3 = this.v;
        this.w = d3 * d3;
        double d4 = this.w;
        this.x = d3 * d4;
        this.y = d4 * d4;
        if (d2 >= 254900.5d && d2 <= 3697000.5d) {
            b();
            dArr[i + 0] = bc.a((this.q - this.u) * j);
            dArr[i + 1] = 0.0d;
            dArr[i + 2] = 0.002569555290487047d;
            return 0;
        }
        if (str == "") {
            str = "";
        }
        String str2 = (((("jd " + d2) + " outside mean node range ") + 254900.5d) + " .. ") + 3697000.5d;
        if (str.length() + str2.length() < 256) {
            StringBuilder sb = new StringBuilder();
            sb.append(str);
            sb.append(str2);
            return -1;
        }
        return -1;
    }

    /* JADX WARN: Removed duplicated region for block: B:33:0x00d0  */
    /* JADX WARN: Removed duplicated region for block: B:37:0x00e8  */
    /*
        Code decompiled incorrectly, please refer to instructions dump.
        To view partially-correct add '--show-bad-code' argument
    */
    private int a(int r20, long r21) {
        /*
            Method dump skipped, instructions count: 250
            To view this dump add '--comments-level debug' option
        */
        throw new UnsupportedOperationException("Method not decompiled: enc.icssoftwares.com.vakkiampro.be.a(int, long):int");
    }

    private int a(int i, long j2, String str) {
        int i2;
        bd.d dVar;
        double[] dArr;
        double[] dArr2;
        double[] dArr3;
        double[] dArr4;
        double[] dArr5;
        int i3;
        int i4;
        bd.d dVar2;
        be beVar;
        double d2;
        bd.a aVar;
        double[] dArr6;
        bd.d dVar3;
        double[] dArr7 = new double[6];
        double[] dArr8 = new double[3];
        double[] dArr9 = new double[6];
        double[] dArr10 = new double[6];
        double[] dArr11 = new double[6];
        double[] dArr12 = new double[6];
        double[] dArr13 = new double[6];
        bd.d dVar4 = this.f675a.d[0];
        if (i > 10000) {
            i2 = d;
            dVar = this.f675a.d[11];
        } else if (i == 12 || i == 13 || i == 14 || i == 15 || i == 16 || i == 17) {
            i2 = e;
            dVar = this.f675a.d[i];
        } else {
            i2 = b;
            dVar = this.f675a.d[i];
        }
        double[] dArr14 = dArr8;
        if ((j2 & (-2049) & (-4097)) == (dVar.y & (-2049) & (-4097))) {
            dVar.y = j2;
            dVar.w = 7 & j2;
            return 0;
        }
        for (int i5 = 0; i5 <= 5; i5++) {
            dArr7[i5] = dVar.x[i5];
        }
        int i6 = ((j2 & 8) > 0L ? 1 : ((j2 & 8) == 0L ? 0 : -1));
        if (i6 != 0) {
            dArr = dArr12;
            if (dVar.w == 1 || dVar.w == 2) {
                for (int i7 = 0; i7 <= 5; i7++) {
                    dArr7[i7] = dArr7[i7] - this.f675a.d[10].x[i7];
                }
            }
        } else {
            dArr = dArr12;
        }
        int i8 = ((32768 & j2) > 0L ? 1 : ((32768 & j2) == 0L ? 0 : -1));
        if (i8 != 0) {
            dArr4 = dArr9;
            if (this.f675a.l.d != dVar4.v || this.f675a.l.d == 0.0d) {
                i4 = i2;
                dVar3 = dVar4;
                dArr5 = dArr10;
                dVar2 = dVar;
                dArr2 = dArr13;
                i3 = 0;
                dArr3 = dArr11;
                if (a(dVar4.v, j2, f, dArr4) != 0) {
                    return -1;
                }
            } else {
                for (int i9 = 0; i9 <= 5; i9++) {
                    dArr4[i9] = this.f675a.l.f[i9];
                }
                i4 = i2;
                dVar3 = dVar4;
                dArr2 = dArr13;
                dArr3 = dArr11;
                dArr5 = dArr10;
                i3 = 0;
                dVar2 = dVar;
            }
            for (int i10 = 0; i10 <= 5; i10++) {
                dArr4[i10] = dArr4[i10] + dVar3.x[i10];
            }
        } else {
            dArr2 = dArr13;
            dArr3 = dArr11;
            dArr4 = dArr9;
            dArr5 = dArr10;
            i3 = 0;
            i4 = i2;
            dVar2 = dVar;
            int i11 = 0;
            for (int i12 = 5; i11 <= i12; i12 = 5) {
                dArr4[i11] = dVar4.x[i11];
                i11++;
            }
        }
        int i13 = ((16 & j2) > 0L ? 1 : ((16 & j2) == 0L ? 0 : -1));
        if (i13 == 0) {
            int i14 = (dVar2.w == 1 || dVar2.w == 2) ? 1 : 0;
            int i15 = ((j2 & 256) > 0L ? 1 : ((j2 & 256) == 0L ? 0 : -1));
            if (i15 != 0) {
                for (int i16 = 0; i16 <= 2; i16++) {
                    double d3 = dArr7[i16] - dArr7[i16 + 3];
                    dArr[i16] = d3;
                    dArr2[i16] = d3;
                }
                int i17 = 0;
                while (i17 <= i14) {
                    for (int i18 = 0; i18 <= 2; i18++) {
                        dArr14[i18] = dArr[i18];
                        if (i6 == 0 && (j2 & 16384) == 0) {
                            dArr14[i18] = dArr14[i18] - (dArr4[i18] - dArr4[i18 + 3]);
                        }
                    }
                    double[] dArr15 = dArr14;
                    double sqrt = ((Math.sqrt(a(dArr15, i3)) * 1.4959787066E11d) / 2.99792458E8d) / 86400.0d;
                    for (int i19 = 0; i19 <= 2; i19++) {
                        dArr[i19] = dArr2[i19] - (dVar2.x[i19 + 3] * sqrt);
                    }
                    i17++;
                    dArr14 = dArr15;
                }
                dArr6 = dArr14;
                for (int i20 = 0; i20 <= 2; i20++) {
                    dArr[i20] = dArr2[i20] - dArr[i20];
                }
            } else {
                dArr6 = dArr14;
            }
            double d4 = 0.0d;
            double d5 = 0.0d;
            for (int i21 = 0; i21 <= i14; i21++) {
                for (int i22 = 0; i22 <= 2; i22++) {
                    dArr6[i22] = dArr7[i22];
                    if (i6 == 0 && (j2 & 16384) == 0) {
                        dArr6[i22] = dArr6[i22] - dArr4[i22];
                    }
                }
                d5 = ((Math.sqrt(a(dArr6, i3)) * 1.4959787066E11d) / 2.99792458E8d) / 86400.0d;
                d4 = dVar2.v - d5;
                for (int i23 = 0; i23 <= 2; i23++) {
                    dArr7[i23] = dVar2.x[i23] - (dVar2.x[i23 + 3] * d5);
                }
            }
            if (i15 != 0) {
                for (int i24 = 0; i24 <= 2; i24++) {
                    dArr[i24] = (dVar2.x[i24] - dArr7[i24]) - dArr[i24];
                }
            }
            if (i15 != 0 && (16392 & j2) == 0) {
                int a2 = i4 == b ? a(d4, i, g, dArr2, dArr3, str) : -2;
                if (a2 != 0) {
                    return a2;
                }
                for (int i25 = 3; i25 <= 5; i25++) {
                    dArr7[i25] = dArr2[i25];
                }
            }
            if (i6 != 0 && (dVar2.w == 1 || dVar2.w == 2)) {
                for (int i26 = 0; i26 <= 5; i26++) {
                    dArr7[i26] = dArr7[i26] - this.f675a.d[10].x[i26];
                }
            }
            beVar = this;
            if (i15 != 0) {
                if (i8 != 0) {
                    if (a(d4, j2, g, dArr5) != 0) {
                        return -1;
                    }
                    for (int i27 = 0; i27 <= 5; i27++) {
                        dArr5[i27] = dArr5[i27] + dArr3[i27];
                    }
                } else {
                    int i28 = 0;
                    for (int i29 = 5; i28 <= i29; i29 = 5) {
                        dArr5[i28] = dArr3[i28];
                        i28++;
                    }
                }
            }
            d2 = d5;
        } else {
            beVar = this;
            d2 = 0.0d;
        }
        if (i6 == 0 && (j2 & 16384) == 0) {
            for (int i30 = 0; i30 <= 5; i30++) {
                dArr7[i30] = dArr7[i30] - dArr4[i30];
            }
            if (i13 == 0 && (j2 & 256) != 0) {
                for (int i31 = 3; i31 <= 5; i31++) {
                    dArr7[i31] = dArr7[i31] - dArr[i31 - 3];
                }
            }
        }
        int i32 = ((j2 & 256) > 0L ? 1 : ((j2 & 256) == 0L ? 0 : -1));
        if (i32 == 0) {
            for (int i33 = 3; i33 <= 5; i33++) {
                dArr7[i33] = 0.0d;
            }
        }
        if (i13 == 0 && (512 & j2) == 0) {
            a(dArr7, d2, j2);
        }
        if (i13 == 0 && (1024 & j2) == 0) {
            double[] dArr16 = dArr4;
            b(dArr7, dArr16, j2);
            if (i32 != 0) {
                for (int i34 = 3; i34 <= 5; i34++) {
                    dArr7[i34] = dArr7[i34] + (dArr16[i34] - dArr5[i34]);
                }
            }
        }
        for (int i35 = 0; i35 <= 5; i35++) {
            dArr2[i35] = dArr7[i35];
        }
        if ((32 & j2) == 0) {
            bc.a(dArr7, i3, dVar2.v, -1);
            if (i32 != 0) {
                a(dArr7, 0, dVar2.v, -1);
            }
            aVar = beVar.f675a.g;
        } else {
            aVar = beVar.f675a.h;
        }
        return a(dVar2, j2, dArr7, dArr2, aVar);
    }

    /* JADX WARN: Code restructure failed: missing block: B:13:0x0056, code lost:
        if (r1 != 2451545.0d) goto L4;
     */
    /* JADX WARN: Removed duplicated region for block: B:18:0x0066  */
    /* JADX WARN: Removed duplicated region for block: B:41:0x012d  */
    /* JADX WARN: Removed duplicated region for block: B:42:0x013b  */
    /*
        Code decompiled incorrectly, please refer to instructions dump.
        To view partially-correct add '--show-bad-code' argument
    */
    private int a(long r23, double r25, double[] r27) {
        /*
            Method dump skipped, instructions count: 340
            To view this dump add '--comments-level debug' option
        */
        throw new UnsupportedOperationException("Method not decompiled: enc.icssoftwares.com.vakkiampro.be.a(long, double, double[]):int");
    }

    private int a(long j2, String str) {
        bd.d dVar;
        bd.d dVar2;
        bd.d dVar3;
        bd.d dVar4;
        double[] dArr;
        bd.a aVar;
        int i;
        bd.d dVar5;
        double[] dArr2;
        double[] dArr3;
        bd.d dVar6;
        double[] dArr4;
        double[] dArr5 = new double[6];
        double[] dArr6 = new double[6];
        double[] dArr7 = new double[6];
        double[] dArr8 = new double[6];
        double[] dArr9 = new double[6];
        bd.d dVar7 = this.f675a.d[0];
        bd.d dVar8 = this.f675a.d[10];
        double[] dArr10 = new double[3];
        if ((j2 & (-2049) & (-4097)) == ((-2049) & dVar7.y & (-4097))) {
            dVar7.y = j2;
            dVar7.w = 7 & j2;
            return 0;
        }
        if ((32768 & j2) != 0) {
            if (this.f675a.l.d != dVar7.v || this.f675a.l.d == 0.0d) {
                dVar2 = dVar8;
                dVar6 = dVar7;
                dArr4 = dArr9;
                if (a(dVar7.v, j2, f, dArr4) != 0) {
                    return -1;
                }
            } else {
                for (int i2 = 0; i2 <= 5; i2++) {
                    dArr9[i2] = this.f675a.l.f[i2];
                }
                dVar6 = dVar7;
                dVar2 = dVar8;
                dArr4 = dArr9;
            }
            int i3 = 0;
            while (i3 <= 5) {
                double[] dArr11 = dArr4;
                dArr11[i3] = dArr11[i3] + dVar6.x[i3];
                i3++;
                dArr4 = dArr11;
            }
            dArr9 = dArr4;
            dVar = dVar6;
        } else {
            dVar = dVar7;
            dVar2 = dVar8;
            for (int i4 = 0; i4 <= 5; i4++) {
                dArr9[i4] = dVar.x[i4];
            }
        }
        if (dVar.w == 4 || (j2 & 16384) != 0) {
            dVar3 = dVar2;
            for (int i5 = 0; i5 <= 5; i5++) {
                dArr5[i5] = dArr9[i5];
            }
        } else {
            for (int i6 = 0; i6 <= 5; i6++) {
                dArr5[i6] = dArr9[i6] - dVar2.x[i6];
            }
            dVar3 = dVar2;
        }
        int i7 = ((j2 & 16) > 0L ? 1 : ((j2 & 16) == 0L ? 0 : -1));
        if (i7 != 0 || (dVar.w != 1 && dVar.w != 2 && (j2 & 8) == 0 && (j2 & 16384) == 0)) {
            dVar4 = dVar;
            dArr = dArr9;
        } else {
            for (int i8 = 0; i8 <= 5; i8++) {
                dArr7[i8] = dArr9[i8];
                if (dVar.w == 4) {
                    dArr8[i8] = 0.0d;
                } else {
                    dArr8[i8] = dVar3.x[i8];
                }
            }
            int i9 = 0;
            int i10 = 0;
            while (i10 <= 1) {
                for (int i11 = 0; i11 <= 2; i11++) {
                    dArr10[i11] = dArr7[i11];
                    if ((j2 & 16384) == 0) {
                        dArr10[i11] = dArr10[i11] - dArr8[i11];
                    }
                }
                double[] dArr12 = dArr10;
                double sqrt = dVar.v - (((Math.sqrt(a(dArr12, 0)) * 1.4959787066E11d) / 2.99792458E8d) / 86400.0d);
                if (((int) dVar.w) != 4) {
                    dArr10 = dArr12;
                    i = i10;
                    dVar5 = dVar;
                    dArr2 = dArr9;
                    dArr3 = dArr8;
                    i9 = -1;
                } else if ((j2 & 8) == 0 && (j2 & 16384) == 0) {
                    dArr10 = dArr12;
                    i = i10;
                    dVar5 = dVar;
                    dArr2 = dArr9;
                    dArr3 = dArr8;
                } else {
                    dArr10 = dArr12;
                    i = i10;
                    dVar5 = dVar;
                    dArr2 = dArr9;
                    dArr3 = dArr8;
                    i9 = a(sqrt, 0, g, dArr7, dArr7, str);
                }
                if (i9 != 0) {
                    return i9;
                }
                i10 = i + 1;
                dArr9 = dArr2;
                dVar = dVar5;
                dArr8 = dArr3;
            }
            dVar4 = dVar;
            dArr = dArr9;
            double[] dArr13 = dArr8;
            for (int i12 = 0; i12 <= 5; i12++) {
                dArr5[i12] = dArr7[i12];
                if ((j2 & 16384) == 0) {
                    dArr5[i12] = dArr5[i12] - dArr13[i12];
                }
            }
        }
        int i13 = ((256 & j2) > 0L ? 1 : ((256 & j2) == 0L ? 0 : -1));
        if (i13 == 0) {
            for (int i14 = 3; i14 <= 5; i14++) {
                dArr5[i14] = 0.0d;
            }
        }
        if ((j2 & 8) == 0 && (j2 & 16384) == 0) {
            for (int i15 = 0; i15 <= 5; i15++) {
                dArr5[i15] = -dArr5[i15];
            }
        }
        if (i7 == 0 && (1024 & j2) == 0) {
            b(dArr5, dArr, j2);
        }
        for (int i16 = 0; i16 <= 5; i16++) {
            dArr6[i16] = dArr5[i16];
        }
        if ((32 & j2) == 0) {
            bc.a(dArr5, 0, dVar4.v, -1);
            if (i13 != 0) {
                a(dArr5, 0, dVar4.v, -1);
            }
            aVar = this.f675a.g;
        } else {
            aVar = this.f675a.h;
        }
        return a(dVar4, j2, dArr5, dArr6, aVar);
    }

    private int a(bd.d dVar, long j2, double[] dArr, double[] dArr2, bd.a aVar) {
        be beVar;
        int i;
        int i2 = ((64 & j2) > 0L ? 1 : ((64 & j2) == 0L ? 0 : -1));
        if (i2 == 0) {
            a(dArr, j2, false);
        }
        for (int i3 = 0; i3 <= 5; i3++) {
            dVar.z[i3 + 18] = dArr[i3];
        }
        bc.a(dArr, 0, dArr, 0, aVar.c, aVar.d);
        int i4 = ((256 & j2) > 0L ? 1 : ((256 & j2) == 0L ? 0 : -1));
        if (i4 != 0) {
            bc.a(dArr, 3, dArr, 3, aVar.c, aVar.d);
        }
        if (i2 == 0) {
            beVar = this;
            bc.a(dArr, 0, dArr, 0, beVar.f675a.i.c, beVar.f675a.i.d);
            if (i4 != 0) {
                bc.a(dArr, 3, dArr, 3, beVar.f675a.i.c, beVar.f675a.i.d);
            }
        } else {
            beVar = this;
        }
        for (int i5 = 0; i5 <= 5; i5++) {
            dVar.z[i5 + 6] = dArr[i5];
        }
        if ((65536 & j2) == 0) {
            i = 0;
        } else if ((beVar.f675a.m.f681a & 256) != 0) {
            i = 0;
            a(dArr2, dVar.z, dVar.z, j2);
        } else {
            i = 0;
            if ((beVar.f675a.m.f681a & 512) != 0) {
                beVar.a(dArr2, dVar.z, j2);
            } else {
                bc.c(dVar.z, 6, dVar.z, 0);
                double[] dArr3 = dVar.z;
                dArr3[0] = dArr3[0] - (beVar.a(dVar.v) * 0.0174532925199433d);
                bc.d(dVar.z, 0, dVar.z, 6);
            }
        }
        bc.c(dVar.z, 18, dVar.z, 12);
        bc.c(dVar.z, 6, dVar.z, i);
        for (int i6 = 0; i6 < 2; i6++) {
            double[] dArr4 = dVar.z;
            dArr4[i6] = dArr4[i6] * 57.2957795130823d;
            double[] dArr5 = dVar.z;
            int i7 = i6 + 3;
            dArr5[i7] = dArr5[i7] * 57.2957795130823d;
            double[] dArr6 = dVar.z;
            int i8 = i6 + 12;
            dArr6[i8] = dArr6[i8] * 57.2957795130823d;
            double[] dArr7 = dVar.z;
            int i9 = i6 + 15;
            dArr7[i9] = dArr7[i9] * 57.2957795130823d;
        }
        dVar.y = j2;
        dVar.w = 7 & j2;
        return i;
    }

    private int a(double[] dArr, double[] dArr2, long j2) {
        double[] dArr3 = new double[6];
        double[] dArr4 = new double[6];
        bd.f fVar = this.f675a.m;
        bd.a aVar = this.f675a.h;
        for (int i = 0; i <= 5; i++) {
            dArr3[i] = dArr[i];
        }
        bc.a(dArr3, 0, dArr3, 0, aVar.c, aVar.d);
        if ((j2 & 256) != 0) {
            bc.a(dArr3, 3, dArr3, 3, aVar.c, aVar.d);
        }
        bc.c(dArr3, 0, dArr3, 0);
        dArr3[0] = dArr3[0] - 1.877670046803984d;
        bc.d(dArr3, 0, dArr3, 0);
        bc.a(dArr3, 0, dArr3, 0, 0.027553530354527005d);
        bc.a(dArr3, 3, dArr3, 3, 0.027553530354527005d);
        bc.c(dArr3, 0, dArr3, 0);
        dArr4[0] = 1.0d;
        dArr4[2] = 0.0d;
        dArr4[1] = 0.0d;
        if (fVar.c != 2451545.0d) {
            bc.a(dArr4, 0, fVar.c, 1);
        }
        bc.a(dArr4, 0, dArr4, 0, aVar.c, aVar.d);
        bc.a(dArr4, 0, dArr4, 0);
        dArr4[0] = dArr4[0] - 1.877670046803984d;
        bc.b(dArr4, 0, dArr4, 0);
        bc.a(dArr4, 0, dArr4, 0, 0.027553530354527005d);
        bc.a(dArr4, 0, dArr4, 0);
        dArr3[0] = dArr3[0] - dArr4[0];
        dArr3[0] = dArr3[0] * 57.2957795130823d;
        dArr3[0] = dArr3[0] - fVar.b;
        dArr3[0] = bc.c(dArr3[0]) * 0.0174532925199433d;
        bc.d(dArr3, 0, dArr2, 0);
        return 0;
    }

    private int a(double[] dArr, double[] dArr2, double[] dArr3, long j2) {
        double[] dArr4 = new double[6];
        bd.f fVar = this.f675a.m;
        bd.a aVar = new bd.a();
        for (int i = 0; i <= 5; i++) {
            dArr4[i] = dArr[i];
        }
        if (fVar.c != 2451545.0d) {
            bc.a(dArr4, 0, fVar.c, -1);
            bc.a(dArr4, 3, fVar.c, -1);
        }
        for (int i2 = 0; i2 <= 5; i2++) {
            dArr3[i2] = dArr4[i2];
        }
        a(this.f675a.m.c, aVar);
        bc.a(dArr4, 0, dArr4, 0, aVar.c, aVar.d);
        if ((j2 & 256) != 0) {
            bc.a(dArr4, 3, dArr4, 3, aVar.c, aVar.d);
        }
        bc.c(dArr4, 0, dArr4, 0);
        dArr4[0] = dArr4[0] - (fVar.b * 0.0174532925199433d);
        bc.d(dArr4, 0, dArr2, 0);
        return 0;
    }

    private void a() {
        for (int i = 0; i < 18; i++) {
            this.f675a.d[i].y = -1L;
        }
        for (int i2 = 0; i2 < 4; i2++) {
            this.f675a.e[i2].y = -1L;
        }
        for (int i3 = 0; i3 < 21; i3++) {
            this.f675a.f[i3].b = 0.0d;
            this.f675a.f[i3].c = -1L;
        }
    }

    private static void a(double d2, bd.a aVar) {
        aVar.f676a = d2;
        aVar.b = bc.d(d2);
        aVar.c = Math.sin(aVar.b);
        aVar.d = Math.cos(aVar.b);
    }

    private void a(double d2, double[] dArr) {
        double d3 = this.f675a.g.c;
        double d4 = this.f675a.g.d;
        double d5 = (d2 - 2415020.0d) / 36525.0d;
        double c2 = bc.c((((((1.44E-5d * d5) + 0.009192d) * d5) + 477198.8491d) * d5) + 296.104608d) * 0.0174532925199433d;
        double sin = Math.sin(c2);
        double cos = Math.cos(c2);
        double d6 = (cos * cos) - (sin * sin);
        double d7 = 1.9E-6d * d5;
        double c3 = bc.c(((((d7 - 0.001436d) * d5) + 445267.1142d) * d5) + 350.737486d) * 0.0349065850398866d;
        double sin2 = Math.sin(c3);
        double cos2 = Math.cos(c3);
        double c4 = bc.c(((((((-3.0E-7d) * d5) - 0.003211d) * d5) + 483202.0251d) * d5) + 11.250889d) * 0.0174532925199433d;
        double sin3 = Math.sin(c4);
        double cos3 = Math.cos(c4);
        double d8 = (cos2 * cos) + (sin2 * sin);
        double sin4 = ((((((((((d7 - 0.001133d) * d5) + 481267.8831d) * d5) + 270.434164d) + (6.28875d * sin)) + (((sin2 * cos) - (cos2 * sin)) * 1.274018d)) + (0.658309d * sin2)) + (((sin * 2.0d) * cos) * 0.213616d)) - (Math.sin(bc.c(((((((-3.3E-6d) * d5) - 1.5E-4d) * d5) + 35999.0498d) * d5) + 358.475833d) * 0.0174532925199433d) * 0.185596d)) - (((2.0d * sin3) * cos3) * 0.114336d);
        double d9 = sin * cos3;
        double d10 = cos * sin3;
        double[] dArr2 = {bc.c(sin4) * 0.0174532925199433d, ((5.128189d * sin3) + ((d9 + d10) * 0.280606d) + ((d9 - d10) * 0.277693d) + (((sin2 * cos3) - (sin3 * cos2)) * 0.173238d)) * 0.0174532925199433d, 4.263523E-5d / Math.sin((((((cos * 0.051818d) + 0.950724d) + (d8 * 0.009531d)) + (cos2 * 0.007843d)) + (d6 * 0.002824d)) * 0.0174532925199433d)};
        bc.b(dArr2, 0, dArr2, 0);
        bc.a(dArr2, 0, dArr2, 0, -d3, d4);
        bc.a(dArr2, 0, d2, 1);
        for (int i = 0; i <= 2; i++) {
            dArr[i] = dArr[i] - (dArr2[i] / 82.30058827479664d);
        }
    }

    private void a(int i, double d2, int i2) {
        double sin = Math.sin(d2);
        double cos = Math.cos(d2);
        double[][] dArr = this.k;
        dArr[i][0] = sin;
        double[][] dArr2 = this.l;
        dArr2[i][0] = cos;
        double d3 = 2.0d * sin * cos;
        double d4 = (cos * cos) - (sin * sin);
        dArr[i][1] = d3;
        dArr2[i][1] = d4;
        int i3 = 2;
        while (i3 < i2) {
            double d5 = (sin * d4) + (cos * d3);
            d4 = (d4 * cos) - (d3 * sin);
            this.k[i][i3] = d5;
            this.l[i][i3] = d4;
            i3++;
            d3 = d5;
        }
    }

    private static void a(bd.c cVar, bd.a aVar) {
        double d2 = cVar.b[0];
        double d3 = aVar.b + cVar.b[1];
        double sin = Math.sin(d2);
        double cos = Math.cos(d2);
        double d4 = aVar.c;
        double d5 = aVar.d;
        double sin2 = Math.sin(d3);
        double cos2 = Math.cos(d3);
        cVar.e[0][0] = cos;
        cVar.e[0][1] = sin * cos2;
        cVar.e[0][2] = sin * sin2;
        double d6 = -sin;
        cVar.e[1][0] = d6 * d5;
        double d7 = cos * cos2;
        cVar.e[1][1] = (d7 * d5) + (sin2 * d4);
        double d8 = cos * sin2;
        cVar.e[1][2] = (d8 * d5) - (cos2 * d4);
        cVar.e[2][0] = d6 * d4;
        cVar.e[2][1] = (d7 * d4) - (sin2 * d5);
        cVar.e[2][2] = (d8 * d4) + (cos2 * d5);
    }

    private void a(double[] dArr, double d2, long j2) {
        int i;
        int i2;
        double[] dArr2 = new double[6];
        double[] dArr3 = new double[6];
        double[] dArr4 = new double[6];
        double[] dArr5 = new double[6];
        double[] dArr6 = new double[6];
        double[] dArr7 = new double[6];
        double[] dArr8 = new double[6];
        bd.d dVar = this.f675a.d[0];
        bd.d dVar2 = this.f675a.d[10];
        long j3 = dVar.w;
        for (int i3 = 0; i3 <= 5; i3++) {
            dArr8[i3] = dVar.x[i3];
        }
        if ((j2 & 32768) != 0) {
            for (int i4 = 0; i4 <= 5; i4++) {
                dArr8[i4] = dArr8[i4] + this.f675a.l.f[i4];
            }
        }
        int i5 = 0;
        while (true) {
            if (i5 > 2) {
                break;
            }
            dArr3[i5] = dArr[i5];
            i5++;
        }
        int i6 = (j3 > 1L ? 1 : (j3 == 1L ? 0 : -1));
        if (i6 == 0 || j3 == 2) {
            for (int i7 = 0; i7 <= 2; i7++) {
                dArr4[i7] = dArr8[i7] - dVar2.x[i7];
            }
        } else {
            for (int i8 = 0; i8 <= 2; i8++) {
                dArr4[i8] = dArr8[i8];
            }
        }
        if (i6 == 0 || j3 == 2) {
            for (int i9 = 0; i9 <= 2; i9++) {
                dArr7[i9] = dVar2.x[i9] - (dVar2.x[i9 + 3] * d2);
            }
            for (int i10 = 3; i10 <= 5; i10++) {
                dArr7[i10] = dVar2.x[i10];
            }
        } else {
            for (int i11 = 0; i11 <= 5; i11++) {
                dArr7[i11] = dVar2.x[i11];
            }
        }
        for (int i12 = 0; i12 <= 2; i12++) {
            dArr5[i12] = (dArr[i12] + dArr8[i12]) - dArr7[i12];
        }
        double sqrt = Math.sqrt(a(dArr3, 0));
        double sqrt2 = Math.sqrt(a(dArr5, 0));
        double sqrt3 = Math.sqrt(a(dArr4, 0));
        for (int i13 = 0; i13 <= 2; i13++) {
            dArr3[i13] = dArr3[i13] / sqrt;
            dArr5[i13] = dArr5[i13] / sqrt2;
            dArr4[i13] = dArr4[i13] / sqrt3;
        }
        double a2 = a(dArr3, dArr5, 0);
        double a3 = a(dArr3, dArr4, 0);
        double a4 = a(dArr5, dArr4, 0);
        double sqrt4 = Math.sqrt(1.0d - (a3 * a3));
        double d3 = 0.004652417528031441d / sqrt3;
        double b2 = (((((sqrt4 < d3 ? b(sqrt4 / d3) : 1.0d) * 2.65424876E20d) / 2.99792458E8d) / 2.99792458E8d) / 1.4959787066E11d) / sqrt3;
        double d4 = a4 + 1.0d;
        for (int i14 = 0; i14 <= 2; i14++) {
            dArr2[i14] = (dArr3[i14] + ((b2 / d4) * ((dArr4[i14] * a2) - (dArr5[i14] * a3)))) * sqrt;
        }
        if ((j2 & 256) != 0) {
            for (int i15 = 0; i15 <= 2; i15++) {
                dArr3[i15] = dArr[i15] - (dArr[i15 + 3] * (-5.0E-7d));
            }
            if (i6 == 0 || j3 == 2) {
                int i16 = 0;
                for (i = 2; i16 <= i; i = 2) {
                    int i17 = i16 + 3;
                    dArr4[i16] = (dArr8[i16] - dVar2.x[i16]) - ((dArr8[i17] - dVar2.x[i17]) * (-5.0E-7d));
                    i16++;
                }
            } else {
                for (int i18 = 0; i18 <= 2; i18++) {
                    dArr4[i18] = dArr8[i18] - (dArr8[i18 + 3] * (-5.0E-7d));
                }
            }
            for (int i19 = 0; i19 <= 2; i19++) {
                int i20 = i19 + 3;
                dArr5[i19] = ((dArr3[i19] + dArr8[i19]) - dArr7[i19]) - ((dArr8[i20] - dArr7[i20]) * (-5.0E-7d));
            }
            double sqrt5 = Math.sqrt(a(dArr3, 0));
            double sqrt6 = Math.sqrt(a(dArr5, 0));
            double sqrt7 = Math.sqrt(a(dArr4, 0));
            for (int i21 = 0; i21 <= 2; i21++) {
                dArr3[i21] = dArr3[i21] / sqrt5;
                dArr5[i21] = dArr5[i21] / sqrt6;
                dArr4[i21] = dArr4[i21] / sqrt7;
            }
            i2 = 0;
            double a5 = a(dArr3, dArr5, 0);
            double a6 = a(dArr3, dArr4, 0);
            double a7 = a(dArr5, dArr4, 0);
            double sqrt8 = Math.sqrt(1.0d - (a6 * a6));
            double d5 = 0.004652417528031441d / sqrt7;
            double b3 = (((((sqrt8 < d5 ? b(sqrt8 / d5) : 1.0d) * 2.65424876E20d) / 2.99792458E8d) / 2.99792458E8d) / 1.4959787066E11d) / sqrt7;
            double d6 = a7 + 1.0d;
            for (int i22 = 0; i22 <= 2; i22++) {
                dArr6[i22] = (dArr3[i22] + ((b3 / d6) * ((dArr4[i22] * a5) - (dArr5[i22] * a6)))) * sqrt5;
            }
            for (int i23 = 0; i23 <= 2; i23++) {
                int i24 = i23 + 3;
                dArr[i24] = dArr[i24] + (((dArr2[i23] - dArr[i23]) - (dArr6[i23] - (dArr3[i23] * sqrt5))) / (-5.0E-7d));
            }
        } else {
            i2 = 0;
        }
        while (i2 <= 2) {
            dArr[i2] = dArr2[i2];
            i2++;
        }
    }

    private void a(double[] dArr, int i, double d2, int i2) {
        double d3;
        bd.a aVar;
        double d4 = (d2 - 2451545.0d) / 36525.0d;
        if (i2 == -1) {
            d3 = 1.0d;
            aVar = this.f675a.g;
        } else {
            d3 = -1.0d;
            aVar = this.f675a.h;
        }
        bd.a aVar2 = aVar;
        int i3 = i + 3;
        bc.a(dArr, i3, d2, i2);
        bc.a(dArr, i, dArr, i, aVar2.c, aVar2.d);
        bc.a(dArr, i3, dArr, i3, aVar2.c, aVar2.d);
        bc.c(dArr, i, dArr, i);
        dArr[i3] = dArr[i3] + (((((d4 * 0.0222226d) + 50.290966d) / 3600.0d) / 365.25d) * 0.0174532925199433d * d3);
        bc.d(dArr, i, dArr, i);
        bc.a(dArr, i, dArr, i, -aVar2.c, aVar2.d);
        bc.a(dArr, i3, dArr, i3, -aVar2.c, aVar2.d);
    }

    private void a(double[] dArr, long j2, boolean z) {
        double[] dArr2 = new double[6];
        double[] dArr3 = new double[6];
        for (int i = 0; i <= 2; i++) {
            if (z) {
                dArr2[i] = (dArr[0] * this.f675a.i.e[i][0]) + (dArr[1] * this.f675a.i.e[i][1]) + (dArr[2] * this.f675a.i.e[i][2]);
            } else {
                dArr2[i] = (dArr[0] * this.f675a.i.e[0][i]) + (dArr[1] * this.f675a.i.e[1][i]) + (dArr[2] * this.f675a.i.e[2][i]);
            }
        }
        if ((j2 & 256) != 0) {
            for (int i2 = 0; i2 <= 2; i2++) {
                if (z) {
                    dArr2[i2 + 3] = (dArr[3] * this.f675a.i.e[i2][0]) + (dArr[4] * this.f675a.i.e[i2][1]) + (dArr[5] * this.f675a.i.e[i2][2]);
                } else {
                    dArr2[i2 + 3] = (dArr[3] * this.f675a.i.e[0][i2]) + (dArr[4] * this.f675a.i.e[1][i2]) + (dArr[5] * this.f675a.i.e[2][i2]);
                }
            }
            for (int i3 = 0; i3 <= 2; i3++) {
                if (z) {
                    dArr3[i3] = (dArr[0] * this.f675a.k.e[i3][0]) + (dArr[1] * this.f675a.k.e[i3][1]) + (dArr[2] * this.f675a.k.e[i3][2]);
                } else {
                    dArr3[i3] = (dArr[0] * this.f675a.k.e[0][i3]) + (dArr[1] * this.f675a.k.e[1][i3]) + (dArr[2] * this.f675a.k.e[2][i3]);
                }
                int i4 = i3 + 3;
                dArr[i4] = dArr2[i4] + ((dArr2[i3] - dArr3[i3]) / 1.0E-4d);
            }
        }
        for (int i5 = 0; i5 <= 2; i5++) {
            dArr[i5] = dArr2[i5];
        }
    }

    private void a(short[] sArr, int i, int i2, double[] dArr) {
        int i3;
        int i4;
        int i5 = i;
        int i6 = 0;
        int i7 = 0;
        while (i6 < i5) {
            double d2 = 0.0d;
            boolean z = false;
            int i8 = i7;
            double d3 = 0.0d;
            int i9 = 0;
            while (i9 < 4) {
                int i10 = i8 + 1;
                short s = sArr[i8];
                if (s != 0) {
                    int i11 = (s < 0 ? -s : s) - 1;
                    double d4 = this.k[i9][i11];
                    double d5 = this.l[i9][i11];
                    if (s < 0) {
                        d4 = -d4;
                    }
                    if (z) {
                        d2 = (d5 * d2) - (d4 * d3);
                        d3 = (d4 * d2) + (d5 * d3);
                    } else {
                        d3 = d4;
                        d2 = d5;
                        z = true;
                    }
                }
                i9++;
                i8 = i10;
            }
            switch (i2) {
                case 1:
                    short s2 = sArr[i8];
                    int i12 = i8 + 1 + 1;
                    dArr[0] = dArr[0] + (((s2 * 10000.0d) + sArr[i3]) * d3);
                    int i13 = i12 + 1;
                    short s3 = sArr[i12];
                    int i14 = i13 + 1;
                    short s4 = sArr[i13];
                    if (s4 != 0) {
                        dArr[2] = dArr[2] + (((s3 * 10000.0d) + s4) * d2);
                    }
                    i7 = i14;
                    continue;
                    i6++;
                    i5 = i;
                case 2:
                    int i15 = i8 + 1;
                    short s5 = sArr[i8];
                    int i16 = i15 + 1;
                    short s6 = sArr[i15];
                    dArr[0] = dArr[0] + (s5 * d3);
                    dArr[2] = dArr[2] + (s6 * d2);
                    i7 = i16;
                    break;
                case 3:
                    i7 = i8 + 1 + 1;
                    dArr[1] = dArr[1] + (((sArr[i8] * 10000.0d) + sArr[i4]) * d3);
                    break;
                case 4:
                    dArr[1] = dArr[1] + (sArr[i8] * d3);
                    i7 = i8 + 1;
                    break;
                default:
                    i7 = i8;
                    continue;
                    i6++;
                    i5 = i;
            }
            i6++;
            i5 = i;
        }
    }

    private static double b(double d2) {
        double[] dArr = {1.0d, 0.99d, 0.98d, 0.97d, 0.96d, 0.95d, 0.94d, 0.93d, 0.92d, 0.91d, 0.9d, 0.89d, 0.88d, 0.87d, 0.86d, 0.85d, 0.84d, 0.83d, 0.82d, 0.81d, 0.8d, 0.79d, 0.78d, 0.77d, 0.76d, 0.75d, 0.74d, 0.73d, 0.72d, 0.71d, 0.7d, 0.69d, 0.68d, 0.67d, 0.66d, 0.65d, 0.64d, 0.63d, 0.62d, 0.61d, 0.6d, 0.59d, 0.58d, 0.57d, 0.56d, 0.55d, 0.54d, 0.53d, 0.52d, 0.51d, 0.5d, 0.49d, 0.48d, 0.47d, 0.46d, 0.45d, 0.44d, 0.43d, 0.42d, 0.41d, 0.4d, 0.39d, 0.38d, 0.37d, 0.36d, 0.35d, 0.34d, 0.33d, 0.32d, 0.31d, 0.3d, 0.29d, 0.28d, 0.27d, 0.26d, 0.25d, 0.24d, 0.23d, 0.22d, 0.21d, 0.2d, 0.19d, 0.18d, 0.17d, 0.16d, 0.15d, 0.14d, 0.13d, 0.12d, 0.11d, 0.1d, 0.09d, 0.08d, 0.07d, 0.06d, 0.05d, 0.04d, 0.03d, 0.02d, 0.01d, 0.0d};
        double[] dArr2 = {1.0d, 0.999979d, 0.99994d, 0.999881d, 0.999811d, 0.999724d, 0.999622d, 0.999497d, 0.999354d, 0.999192d, 0.999d, 0.998786d, 0.998535d, 0.998242d, 0.997919d, 0.997571d, 0.997198d, 0.996792d, 0.996316d, 0.995791d, 0.995226d, 0.994625d, 0.993991d, 0.993326d, 0.992598d, 0.99177d, 0.990873d, 0.989919d, 0.988912d, 0.987856d, 0.986755d, 0.98561d, 0.984398d, 0.982986d, 0.981437d, 0.979779d, 0.978024d, 0.976182d, 0.974256d, 0.972253d, 0.970174d, 0.968024d, 0.965594d, 0.962797d, 0.959758d, 0.956515d, 0.953088d, 0.949495d, 0.945741d, 0.941838d, 0.93779d, 0.933563d, 0.928668d, 0.923288d, 0.917527d, 0.911432d, 0.905035d, 0.898353d, 0.891022d, 0.88294d, 0.874312d, 0.865206d, 0.855423d, 0.844619d, 0.833074d, 0.820876d, 0.808031d, 0.793962d, 0.778931d, 0.763021d, 0.745815d, 0.727557d, 0.708234d, 0.687583d, 0.665741d, 0.642597d, 0.618252d, 0.592586d, 0.565747d, 0.537697d, 0.508554d, 0.47842d, 0.447322d, 0.415454d, 0.382892d, 0.349955d, 0.316691d, 0.283565d, 0.250431d, 0.218327d, 0.186794d, 0.156287d, 0.128421d, 0.102237d, 0.077393d, 0.054833d, 0.036361d, 0.020953d, 0.009645d, 0.002767d, 0.0d};
        if (d2 <= 0.0d) {
            return 0.0d;
        }
        if (d2 >= 1.0d) {
            return 1.0d;
        }
        int i = 0;
        while (dArr[i] > d2) {
            i++;
        }
        int i2 = i - 1;
        return dArr2[i2] + (((d2 - dArr[i2]) / (dArr[i] - dArr[i2])) * (dArr2[i] - dArr2[i2]));
    }

    private int b(double d2, int i, double[] dArr) {
        bg a2;
        double[] dArr2;
        byte b2;
        double d3;
        double[] dArr3;
        int i2;
        double[] dArr4 = {5.38101628688982E10d, 2.10664136433548E10d, 1.29597742283429E10d, 6.8905077493988E9d, 1.0925660377991E9d, 4.399609855372E8d, 1.542481193933E8d, 7.86550320744E7d, 5.22722451795E7d};
        double[] dArr5 = {908103.259872d, 655127.28306d, 361679.244588d, 1279558.798488d, 123665.46746400002d, 180278.79948000002d, 1130598.0183960001d, 1095655.195728d, 860492.1546d};
        switch (i) {
            case 0:
                a2 = aw.a();
                break;
            case 1:
                a2 = bb.a();
                break;
            case 2:
                a2 = at.a();
                break;
            case 3:
                a2 = av.a();
                break;
            case 4:
                a2 = au.a();
                break;
            case 5:
                a2 = az.a();
                break;
            case 6:
                a2 = ba.a();
                break;
            case 7:
                a2 = ax.a();
                break;
            case 8:
                a2 = ay.a();
                break;
            default:
                a2 = null;
                break;
        }
        byte[] bArr = a2.f684a;
        double d4 = a2.g;
        double d5 = (d2 - 2451545.0d) / 3652500.0d;
        for (int i3 = 0; i3 < 9; i3++) {
            byte b3 = bArr[i3];
            if (b3 > 0) {
                a(i3, (c(dArr4[i3] * d5) + dArr5[i3]) * j, b3);
            }
        }
        byte[] bArr2 = a2.c;
        double[] dArr6 = a2.d;
        double[] dArr7 = a2.e;
        double[] dArr8 = a2.f;
        int i4 = 0;
        double d6 = 0.0d;
        double d7 = 0.0d;
        double d8 = 0.0d;
        int i5 = 0;
        int i6 = 0;
        int i7 = 0;
        while (true) {
            int i8 = i4 + 1;
            byte b4 = bArr2[i4];
            if (b4 < 0) {
                double d9 = d4;
                double d10 = j;
                dArr[0] = d6 * d10;
                dArr[1] = d7 * d10;
                dArr[2] = (d10 * d9 * d8) + d9;
                return 0;
            } else if (b4 == 0) {
                i4 = i8 + 1;
                byte b5 = bArr2[i8];
                double d11 = dArr6[i5];
                i5++;
                int i9 = 0;
                while (i9 < b5) {
                    d11 = (d11 * d5) + dArr6[i5];
                    i9++;
                    i5++;
                }
                d6 += c(d11);
                double d12 = dArr7[i6];
                i6++;
                int i10 = 0;
                while (i10 < b5) {
                    d12 = (d12 * d5) + dArr7[i6];
                    i10++;
                    i6++;
                }
                d7 += d12;
                int i11 = i7 + 1;
                double d13 = dArr8[i7];
                int i12 = i11;
                int i13 = 0;
                while (i13 < b5) {
                    d13 = (d13 * d5) + dArr8[i12];
                    i13++;
                    i12++;
                }
                d8 += d13;
                i7 = i12;
            } else {
                int i14 = 0;
                boolean z = false;
                double d14 = 0.0d;
                double d15 = 0.0d;
                while (i14 < b4) {
                    int i15 = i8 + 1;
                    byte b6 = bArr2[i8];
                    i8 = i15 + 1;
                    int i16 = bArr2[i15] - 1;
                    if (b6 != 0) {
                        if (b6 < 0) {
                            b2 = b4;
                            i2 = -b6;
                        } else {
                            b2 = b4;
                            i2 = b6;
                        }
                        int i17 = i2 - 1;
                        d3 = d4;
                        dArr3 = dArr7;
                        dArr2 = dArr8;
                        double d16 = this.k[i16][i17];
                        if (b6 < 0) {
                            d16 = -d16;
                        }
                        double d17 = this.l[i16][i17];
                        if (z) {
                            d15 = (d17 * d15) - (d16 * d14);
                            d14 = (d16 * d15) + (d17 * d14);
                        } else {
                            d14 = d16;
                            d15 = d17;
                            z = true;
                        }
                    } else {
                        dArr2 = dArr8;
                        b2 = b4;
                        d3 = d4;
                        dArr3 = dArr7;
                    }
                    i14++;
                    dArr7 = dArr3;
                    b4 = b2;
                    d4 = d3;
                    dArr8 = dArr2;
                }
                double[] dArr9 = dArr8;
                double d18 = d4;
                double[] dArr10 = dArr7;
                i4 = i8 + 1;
                byte b7 = bArr2[i8];
                int i18 = i5 + 1;
                double d19 = dArr6[i5];
                double d20 = dArr6[i18];
                i5 = i18 + 1;
                for (int i19 = 0; i19 < b7; i19++) {
                    int i20 = i5 + 1;
                    d19 = (d19 * d5) + dArr6[i5];
                    i5 = i20 + 1;
                    d20 = (d20 * d5) + dArr6[i20];
                }
                d6 += (d19 * d15) + (d20 * d14);
                int i21 = i6 + 1;
                double d21 = dArr10[i6];
                double d22 = dArr10[i21];
                i6 = i21 + 1;
                for (int i22 = 0; i22 < b7; i22++) {
                    int i23 = i6 + 1;
                    d21 = (d21 * d5) + dArr10[i6];
                    i6 = i23 + 1;
                    d22 = (d22 * d5) + dArr10[i23];
                }
                d7 += (d21 * d15) + (d22 * d14);
                int i24 = i7 + 1;
                double d23 = dArr9[i7];
                int i25 = i24 + 1;
                double d24 = dArr9[i24];
                for (int i26 = 0; i26 < b7; i26++) {
                    int i27 = i25 + 1;
                    d23 = (d23 * d5) + dArr9[i25];
                    i25 = i27 + 1;
                    d24 = (d24 * d5) + dArr9[i27];
                }
                d8 += (d23 * d15) + (d24 * d14);
                i7 = i25;
                dArr7 = dArr10;
                d4 = d18;
                dArr8 = dArr9;
            }
        }
    }

    private int b(double d2, double[] dArr) {
        this.v = (d2 - 2451545.0d) / 36525.0d;
        double d3 = this.v;
        this.w = d3 * d3;
        b();
        this.B = c((this.v * 2.106641364335482E8d) + 655127.283046d);
        double d4 = this.B;
        double d5 = this.v;
        this.B = d4 + ((((((((((((((((((-9.36E-23d) * d5) - 1.95E-20d) * d5) + 6.097E-18d) * d5) + 4.43201E-15d) * d5) + 2.509418E-13d) * d5) - 3.0622898E-10d) * d5) - 2.26602516E-9d) * d5) - 1.4244812531E-5d) * d5) + 0.005871373088d) * this.w);
        this.C = c((d5 * 1.2959774226669231E8d) + 361679.214649d);
        double d6 = this.C;
        double d7 = this.v;
        this.C = d6 + ((((((((((((((((((-1.16E-22d) * d7) + 2.976E-19d) * d7) + 2.846E-17d) * d7) - 1.08402E-14d) * d7) - 1.226182E-12d) * d7) + 1.7228268E-10d) * d7) + 1.515912254E-7d) * d7) + 8.863982531E-6d) * d7) - 0.020199859001d) * this.w);
        this.D = c((d7 * 6.890507759284E7d) + 1279559.78866d);
        double d8 = this.D;
        double d9 = this.v;
        this.D = d8 + ((((-1.043E-5d) * d9) + 0.00938012d) * this.w);
        this.E = c((d9 * 1.0925660428608E7d) + 123665.34212d);
        double d10 = this.E;
        double d11 = this.v;
        this.E = d10 + (((1.543273E-5d * d11) - 0.306037836351d) * this.w);
        this.F = c((d11 * 4399609.65932d) + 180278.89694d);
        double d12 = this.F;
        double d13 = this.v;
        this.F = d12 + (((((4.475946E-8d * d13) - 6.874806E-5d) * d13) + 0.756161437443d) * this.w);
        a(0, j * this.t, 6);
        a(1, j * this.r, 4);
        a(2, j * this.s, 4);
        a(3, j * this.u, 4);
        this.p = new double[3];
        double[] dArr2 = this.p;
        dArr2[0] = 0.0d;
        dArr2[1] = 0.0d;
        dArr2[2] = 0.0d;
        a(new short[]{0, 1, 0, 0, 487, -36, 2, -1, -1, 0, -150, 111, 2, -1, 0, 0, -120, 149, 0, 1, -1, 0, 108, 95, 0, 1, 1, 0, 80, -77, 2, 1, -1, 0, 21, -18, 2, 1, 0, 0, 20, -23, 1, 1, 0, 0, -13, 12, 2, -2, 0, 0, -12, 14, 2, -1, 1, 0, -11, 9, 2, -2, -1, 0, -11, 7, 0, 2, 0, 0, 11, 0, 2, -1, -2, 0, -6, -7, 0, 1, -2, 0, 7, 5, 0, 1, 2, 0, 6, -4, 2, 2, -1, 0, 5, -3, 0, 2, -1, 0, 5, 3, 4, -1, -1, 0, -3, 3, 2, 0, 0, 0, 3, -4, 4, -1, -2, 0, -2, 0, 2, 1, -2, 0, -2, 0, 2, -1, 0, -2, -2, 0, 2, 1, 1, 0, 2, -2, 2, 0, -1, 0, 2, 0, 0, 2, 1, 0, 2, 0}, 25, 2, dArr2);
        a(new short[]{2, -1, 0, -1, -22, 2, 1, 0, -1, 9, 2, -1, 0, 1, -6, 2, -1, -1, 1, -6, 2, -1, -1, -1, -5, 0, 1, 0, 1, 5, 0, 1, -1, -1, 5, 0, 1, 1, 1, 4, 0, 1, 1, -1, 4, 0, 1, 0, -1, 4, 0, 1, -1, 1, 4, 2, -2, 0, -1, -2}, 12, 4, this.p);
        this.z = (this.B * 18.0d) - (this.C * 16.0d);
        this.A = j * (this.z - this.s);
        this.G = Math.cos(this.A);
        this.H = Math.sin(this.A);
        double d14 = this.G;
        double d15 = this.H;
        this.n = (6.367278d * d14) + (12.747036d * d15);
        this.I = (23123.7d * d14) - (10570.02d * d15);
        double[] dArr3 = m;
        this.J = (dArr3[12] * d14) + (dArr3[13] * d15);
        double[] dArr4 = this.p;
        dArr4[2] = dArr4[2] + (d14 * 5.01d) + (d15 * 2.72d);
        this.A = j * (((this.B * 10.0d) - (this.C * 3.0d)) - this.s);
        this.G = Math.cos(this.A);
        this.H = Math.sin(this.A);
        double d16 = this.n;
        double d17 = this.G;
        double d18 = this.H;
        this.n = d16 + ((-0.253102d) * d17) + (0.503359d * d18);
        this.I += (1258.46d * d17) + (707.29d * d18);
        double d19 = this.J;
        double[] dArr5 = m;
        this.J = d19 + (dArr5[14] * d17) + (dArr5[15] * d18);
        this.A = j * ((this.B * 8.0d) - (this.C * 13.0d));
        this.G = Math.cos(this.A);
        this.H = Math.sin(this.A);
        double d20 = this.n;
        double d21 = this.G;
        double d22 = this.H;
        this.n = d20 + (((-0.187231d) * d21) - (0.127481d * d22));
        this.I += ((-319.87d) * d21) - (18.34d * d22);
        double d23 = this.J;
        double[] dArr6 = m;
        this.J = d23 + (dArr6[16] * d21) + (dArr6[17] * d22);
        double d24 = ((this.C * 4.0d) - (this.D * 8.0d)) + (this.E * 3.0d);
        this.A = j * d24;
        this.G = Math.cos(this.A);
        this.H = Math.sin(this.A);
        double d25 = this.n;
        double d26 = this.G;
        double d27 = this.H;
        this.n = d25 + ((-0.866287d) * d26) + (0.248192d * d27);
        this.I += (41.87d * d26) + (1053.97d * d27);
        double d28 = this.J;
        double[] dArr7 = m;
        this.J = d28 + (dArr7[18] * d26) + (dArr7[19] * d27);
        this.A = j * (d24 - this.s);
        this.G = Math.cos(this.A);
        this.H = Math.sin(this.A);
        double d29 = this.n;
        double d30 = this.G;
        double d31 = this.H;
        this.n = d29 + (d30 * (-0.165009d)) + (d31 * 0.044176d);
        this.I += (d30 * 4.67d) + (d31 * 201.55d);
        this.A = j * this.z;
        this.G = Math.cos(this.A);
        this.H = Math.sin(this.A);
        double d32 = this.n;
        double d33 = this.G;
        double d34 = this.H;
        this.n = d32 + (0.330401d * d33) + (0.661362d * d34);
        this.I += (1202.67d * d33) - (555.59d * d34);
        double d35 = this.J;
        double[] dArr8 = m;
        this.J = d35 + (dArr8[20] * d33) + (dArr8[21] * d34);
        this.A = j * (this.z - (this.s * 2.0d));
        this.G = Math.cos(this.A);
        this.H = Math.sin(this.A);
        double d36 = this.n;
        double d37 = this.G;
        double d38 = this.H;
        this.n = d36 + (0.352185d * d37) + (0.705041d * d38);
        this.I += (d37 * 1283.59d) - (d38 * 586.43d);
        this.A = j * ((this.E * 2.0d) - (this.F * 5.0d));
        this.G = Math.cos(this.A);
        this.H = Math.sin(this.A);
        double d39 = this.n;
        double d40 = this.G;
        double d41 = this.H;
        this.n = d39 + ((-0.0347d) * d40) + (0.160041d * d41);
        double d42 = this.J;
        double[] dArr9 = m;
        this.J = d42 + (dArr9[22] * d40) + (dArr9[23] * d41);
        this.A = j * (this.q - this.u);
        this.G = Math.cos(this.A);
        this.H = Math.sin(this.A);
        double d43 = this.n;
        double d44 = this.H;
        this.n = d43 + (this.G * 1.16E-4d) + (7.06304d * d44);
        this.I += d44 * 298.8d;
        this.H = Math.sin(j * this.r);
        this.K = m[24] * this.H;
        this.L = 0.0d;
        this.A = j * ((this.t * 2.0d) - this.r);
        this.H = Math.sin(this.A);
        this.G = Math.cos(this.A);
        double[] dArr10 = this.p;
        dArr10[2] = dArr10[2] + (this.G * (-0.2655d) * this.v);
        this.A = j * (this.r - this.s);
        dArr10[2] = dArr10[2] + (Math.cos(this.A) * (-0.1568d) * this.v);
        this.A = j * (this.r + this.s);
        double[] dArr11 = this.p;
        dArr11[2] = dArr11[2] + (Math.cos(this.A) * 0.1309d * this.v);
        this.A = j * (((this.t + this.r) * 2.0d) - this.s);
        this.H = Math.sin(this.A);
        this.G = Math.cos(this.A);
        double[] dArr12 = this.p;
        dArr12[2] = dArr12[2] + (this.G * 0.5568d * this.v);
        this.J += dArr12[0];
        this.A = j * (((this.t * 2.0d) - this.r) - this.s);
        double d45 = dArr12[2];
        double d46 = this.v;
        dArr12[2] = d45 + (Math.cos(this.A) * (-0.191d) * d46);
        double[] dArr13 = this.p;
        dArr13[1] = dArr13[1] * d46;
        dArr13[2] = dArr13[2] * d46;
        dArr13[0] = 0.0d;
        a(new short[]{2, -1, 0, -1, -7430, 2, 1, 0, -1, 3043, 2, -1, -1, 1, -2229, 2, -1, 0, 1, -1999, 2, -1, -1, -1, -1869, 0, 1, -1, -1, 1696, 0, 1, 0, 1, 1623, 0, 1, -1, 1, 1418, 0, 1, 1, 1, 1339, 0, 1, 1, -1, 1278, 0, 1, 0, -1, 1217, 2, -2, 0, -1, -547, 2, -1, 1, -1, -443, 2, 1, -1, 1, 331, 2, 1, 0, 1, 317, 2, 0, 0, -1, 295}, 16, 4, dArr13);
        a(new short[]{0, 1, 0, 0, 16, 7680, -1, -2302, 2, -1, -1, 0, -5, -1642, 3, 8245, 2, -1, 0, 0, -4, -1383, 5, 1395, 0, 1, -1, 0, 3, 7115, 3, 2654, 0, 1, 1, 0, 2, 7560, -2, -6396, 2, 1, -1, 0, 0, 7118, 0, -6068, 2, 1, 0, 0, 0, 6128, 0, -7754, 1, 1, 0, 0, 0, -4516, 0, 4194, 2, -2, 0, 0, 0, -4048, 0, 4970, 0, 2, 0, 0, 0, 3747, 0, -540, 2, -2, -1, 0, 0, -3707, 0, 2490, 2, -1, 1, 0, 0, -3649, 0, 3222, 0, 1, -2, 0, 0, 2438, 0, 1760, 2, -1, -2, 0, 0, -2165, 0, -2530, 0, 1, 2, 0, 0, 1923, 0, -1450, 0, 2, -1, 0, 0, 1292, 0, 1070, 2, 2, -1, 0, 0, 1271, 0, -6070, 4, -1, -1, 0, 0, -1098, 0, 990, 2, 0, 0, 0, 0, 1073, 0, -1360, 2, 0, -1, 0, 0, 839, 0, -630, 2, 1, 1, 0, 0, 734, 0, -660, 4, -1, -2, 0, 0, -688, 0, 480, 2, 1, -2, 0, 0, -630, 0, 0, 0, 2, 1, 0, 0, 587, 0, -590, 2, -1, 0, -2, 0, -540, 0, -170, 4, -1, 0, 0, 0, -468, 0, 390, 2, -2, 1, 0, 0, -378, 0, 330, 2, 1, 0, -2, 0, 364, 0, 0, 1, 1, 1, 0, 0, -317, 0, 240, 2, -1, 2, 0, 0, -295, 0, 210, 1, 1, -1, 0, 0, -270, 0, -210, 2, -3, 0, 0, 0, -256, 0, 310, 2, -3, -1, 0, 0, -187, 0, 110, 0, 1, -3, 0, 0, 169, 0, 110, 4, 1, -1, 0, 0, 158, 0, -150, 4, -2, -1, 0, 0, -155, 0, 140, 0, 0, 1, 0, 0, 155, 0, -250, 2, -2, -2, 0, 0, -148, 0, -170}, 38, 1, this.p);
        this.A = j * (((this.z - this.s) - this.u) - 2355767.6d);
        double[] dArr14 = this.p;
        dArr14[1] = dArr14[1] + (Math.sin(this.A) * (-1127.0d));
        this.A = j * (((this.z - this.s) + this.u) - 235353.6d);
        double[] dArr15 = this.p;
        dArr15[1] = dArr15[1] + (Math.sin(this.A) * (-1123.0d));
        this.A = j * (this.C + this.t + 51987.6d);
        double[] dArr16 = this.p;
        dArr16[1] = dArr16[1] + (Math.sin(this.A) * 1303.0d);
        this.A = j * this.q;
        double[] dArr17 = this.p;
        dArr17[1] = dArr17[1] + (Math.sin(this.A) * 342.0d);
        this.A = j * ((this.B * 2.0d) - (this.C * 3.0d));
        this.G = Math.cos(this.A);
        this.H = Math.sin(this.A);
        double d47 = this.n;
        double d48 = this.G;
        double d49 = this.H;
        this.n = d47 + (((-0.34355d) * d48) - (2.76E-4d * d49));
        this.I += (d48 * 105.9d) + (d49 * 336.53d);
        this.A = j * (this.z - (this.t * 2.0d));
        this.G = Math.cos(this.A);
        this.H = Math.sin(this.A);
        double d50 = this.n;
        double d51 = this.G;
        double d52 = this.H;
        this.n = d50 + (0.074668d * d51) + (0.149501d * d52);
        this.I += (d51 * 271.77d) - (d52 * 124.2d);
        this.A = j * ((this.z - (this.t * 2.0d)) - this.s);
        this.G = Math.cos(this.A);
        this.H = Math.sin(this.A);
        double d53 = this.n;
        double d54 = this.G;
        double d55 = this.H;
        this.n = d53 + (0.073444d * d54) + (0.147094d * d55);
        this.I += (d54 * 265.24d) - (d55 * 121.16d);
        this.A = j * ((this.z + (this.t * 2.0d)) - this.s);
        this.G = Math.cos(this.A);
        this.H = Math.sin(this.A);
        double d56 = this.n;
        double d57 = this.G;
        double d58 = this.H;
        this.n = d56 + (0.072844d * d57) + (0.145829d * d58);
        this.I += (d57 * 265.18d) - (d58 * 121.29d);
        this.A = j * (this.z + ((this.t - this.s) * 2.0d));
        this.G = Math.cos(this.A);
        this.H = Math.sin(this.A);
        double d59 = this.n;
        double d60 = this.G;
        double d61 = this.H;
        this.n = d59 + (0.070201d * d60) + (0.140542d * d61);
        this.I += (d60 * 255.36d) - (d61 * 116.79d);
        this.A = j * ((this.C + this.t) - this.u);
        this.G = Math.cos(this.A);
        this.H = Math.sin(this.A);
        double d62 = this.n;
        double d63 = this.G;
        double d64 = this.H;
        this.n = d62 + ((0.288209d * d63) - (0.025901d * d64));
        this.I += (d63 * (-63.51d)) - (d64 * 240.14d);
        this.A = j * ((((this.C * 2.0d) - (this.E * 3.0d)) + (this.t * 2.0d)) - this.s);
        this.G = Math.cos(this.A);
        this.H = Math.sin(this.A);
        double d65 = this.n;
        double d66 = this.G;
        double d67 = this.H;
        this.n = d65 + (0.077865d * d66) + (0.43846d * d67);
        this.I += (d66 * 210.57d) + (d67 * 124.84d);
        this.A = j * (this.C - (this.D * 2.0d));
        this.G = Math.cos(this.A);
        this.H = Math.sin(this.A);
        double d68 = this.n;
        double d69 = this.G;
        double d70 = this.H;
        this.n = d68 + ((-0.216579d) * d69) + (0.241702d * d70);
        this.I += (d69 * 197.67d) + (d70 * 125.23d);
        this.A = j * (this.s + d24);
        this.G = Math.cos(this.A);
        this.H = Math.sin(this.A);
        double d71 = this.n;
        double d72 = this.G;
        double d73 = this.H;
        this.n = d71 + ((-0.165009d) * d72) + (0.044176d * d73);
        this.I += (d72 * 4.67d) + (d73 * 201.55d);
        this.A = j * (((this.t * 2.0d) + d24) - this.s);
        this.G = Math.cos(this.A);
        this.H = Math.sin(this.A);
        double d74 = this.n;
        double d75 = this.G;
        double d76 = this.H;
        this.n = d74 + ((-0.133533d) * d75) + (0.041116d * d76);
        this.I += (d75 * 6.95d) + (d76 * 187.07d);
        this.A = j * ((d24 - (this.t * 2.0d)) + this.s);
        this.G = Math.cos(this.A);
        this.H = Math.sin(this.A);
        double d77 = this.n;
        double d78 = this.G;
        double d79 = this.H;
        this.n = d77 + ((-0.13343d) * d78) + (0.041079d * d79);
        this.I += (d78 * 6.28d) + (d79 * 169.08d);
        this.A = j * ((this.B * 3.0d) - (this.C * 4.0d));
        this.G = Math.cos(this.A);
        this.H = Math.sin(this.A);
        double d80 = this.n;
        double d81 = this.G;
        double d82 = this.H;
        this.n = d80 + ((-0.175074d) * d81) + (0.003035d * d82);
        this.I += (d81 * 49.17d) + (d82 * 150.57d);
        this.A = j * (((((this.C + this.t) - this.s) * 2.0d) - (this.E * 3.0d)) + 213534.0d);
        this.I += Math.sin(this.A) * 158.4d;
        double d83 = this.I;
        double[] dArr18 = this.p;
        this.I = d83 + dArr18[0];
        double d84 = this.v * 0.1d;
        dArr18[1] = dArr18[1] * d84;
        dArr18[2] = dArr18[2] * d84;
        this.A = j * (((((this.C - this.E) + this.t) * 2.0d) - this.s) + 648431.172d);
        this.n += Math.sin(this.A) * 1.14307d;
        this.A = j * ((this.B - this.C) + 648035.568d);
        this.n += Math.sin(this.A) * 0.82155d;
        this.A = j * (((((this.B - this.C) * 3.0d) + (this.t * 2.0d)) - this.s) + 647933.184d);
        this.n += Math.sin(this.A) * 0.64371d;
        this.A = j * ((this.C - this.E) + 4424.04d);
        this.n += Math.sin(this.A) * 0.6388d;
        this.A = j * (((this.q + this.s) - this.u) + 4.68d);
        this.n += Math.sin(this.A) * 0.49331d;
        this.A = j * (((this.q - this.s) - this.u) + 4.68d);
        this.n += Math.sin(this.A) * 0.4914d;
        this.A = j * (this.q + this.u + 2.52d);
        this.n += Math.sin(this.A) * 0.36061d;
        this.A = j * (((this.B * 2.0d) - (this.C * 2.0d)) + 736.2d);
        this.n += Math.sin(this.A) * 0.30154d;
        this.A = j * (((((this.C * 2.0d) - (this.E * 3.0d)) + (this.t * 2.0d)) - (this.s * 2.0d)) + 36138.2d);
        this.n += Math.sin(this.A) * 0.28282d;
        this.A = j * (((((this.C * 2.0d) - (this.E * 2.0d)) + (this.t * 2.0d)) - (this.s * 2.0d)) + 311.0d);
        this.n += Math.sin(this.A) * 0.24516d;
        this.A = j * (((this.C - this.E) - (this.t * 2.0d)) + this.s + 6275.88d);
        this.n += Math.sin(this.A) * 0.21117d;
        this.A = j * (((this.C - this.D) * 2.0d) - 846.36d);
        this.n += Math.sin(this.A) * 0.19444d;
        this.A = j * (((this.C - this.E) * 2.0d) + 1569.96d);
        this.n -= Math.sin(this.A) * 0.18457d;
        this.A = j * ((((this.C - this.E) * 2.0d) - this.s) - 55.8d);
        this.n += Math.sin(this.A) * 0.18256d;
        this.A = j * (((this.C - this.E) - (this.t * 2.0d)) + 6490.08d);
        this.n += Math.sin(this.A) * 0.16499d;
        this.A = j * ((this.C - (this.E * 2.0d)) - 212378.4d);
        this.n += Math.sin(this.A) * 0.16427d;
        this.A = j * ((((this.B - this.C) - this.t) * 2.0d) + this.s + 1122.48d);
        this.n += Math.sin(this.A) * 0.16088d;
        this.A = j * (((this.B - this.C) - this.s) + 32.04d);
        this.n -= Math.sin(this.A) * 0.1535d;
        this.A = j * (((this.C - this.E) - this.s) + 4488.88d);
        this.n += Math.sin(this.A) * 0.14346d;
        this.A = j * (((((this.B - this.C) + this.t) * 2.0d) - this.s) - 8.64d);
        this.n += Math.sin(this.A) * 0.13594d;
        this.A = j * ((((this.B - this.C) - this.t) * 2.0d) + 1319.76d);
        this.n += Math.sin(this.A) * 0.13432d;
        this.A = j * ((((this.B - this.C) - (this.t * 2.0d)) + this.s) - 56.16d);
        this.n -= Math.sin(this.A) * 0.13122d;
        this.A = j * ((this.B - this.C) + this.s + 54.36d);
        this.n -= Math.sin(this.A) * 0.12722d;
        this.A = j * ((((this.B - this.C) * 3.0d) - this.s) + 433.8d);
        this.n += Math.sin(this.A) * 0.12539d;
        this.A = j * ((this.C - this.E) + this.s + 4002.12d);
        this.n += Math.sin(this.A) * 0.10994d;
        this.A = j * (((((this.B * 20.0d) - (this.C * 21.0d)) - (this.t * 2.0d)) + this.s) - 317511.72d);
        this.n += Math.sin(this.A) * 0.10652d;
        this.A = j * ((((this.B * 26.0d) - (this.C * 29.0d)) - this.s) + 270002.52d);
        this.n += Math.sin(this.A) * 0.1049d;
        this.A = j * (((((this.B * 3.0d) - (this.C * 4.0d)) + this.t) - this.s) - 322765.56d);
        this.n += Math.sin(this.A) * 0.10386d;
        this.A = j * (this.q + 648002.556d);
        this.o = Math.sin(this.A) * 8.04508d;
        this.A = j * (this.C + this.t + 996048.252d);
        this.o += Math.sin(this.A) * 1.51021d;
        this.A = j * ((this.z - this.s) + this.u + 95554.332d);
        this.o += Math.sin(this.A) * 0.63037d;
        this.A = j * (((this.z - this.s) - this.u) + 95553.792d);
        this.o += Math.sin(this.A) * 0.63014d;
        this.A = j * ((this.q - this.s) + 2.9d);
        this.o += Math.sin(this.A) * 0.45587d;
        this.A = j * (this.q + this.s + 2.5d);
        this.o += Math.sin(this.A) * (-0.41573d);
        this.A = j * ((this.q - (this.u * 2.0d)) + 3.2d);
        this.o += Math.sin(this.A) * 0.32623d;
        this.A = j * ((this.q - (this.t * 2.0d)) + 2.5d);
        this.o += Math.sin(this.A) * 0.29855d;
        double[] dArr19 = this.p;
        dArr19[0] = 0.0d;
        a(new short[]{0, 0, 1, 0, 22639, 5858, -20905, -3550, 2, 0, -1, 0, 4586, 4383, -3699, -1109, 2, 0, 0, 0, 2369, 9139, -2955, -9676, 0, 0, 2, 0, 769, 257, -569, -9251, 0, 1, 0, 0, -666, -4171, 48, 8883, 0, 0, 0, 2, -411, -5957, -3, -1483, 2, 0, -2, 0, 211, 6556, 246, 1585, 2, -1, -1, 0, 205, 4358, -152, -1377, 2, 0, 1, 0, 191, 9562, -170, -7331, 2, -1, 0, 0, 164, 7285, -204, -5860, 0, 1, -1, 0, -147, -3213, -129, -6201, 1, 0, 0, 0, -124, -9881, 108, 7427, 0, 1, 1, 0, -109, -3803, 104, 7552, 2, 0, 0, -2, 55, 1771, 10, 3211, 0, 0, 1, 2, -45, -996, 0, 0, 0, 0, 1, -2, 39, 5333, 79, 6606, 4, 0, -1, 0, 38, 4298, -34, -7825, 0, 0, 3, 0, 36, 1238, -23, -2104, 4, 0, -2, 0, 30, 7726, -21, -6363, 2, 1, -1, 0, -28, -3971, 24, 2085, 2, 1, 0, 0, -24, -3582, 30, 8238, 1, 0, -1, 0, -18, -5847, -8, -3791, 1, 1, 0, 0, 17, 9545, -16, -6747, 2, -1, 1, 0, 14, 5303, -12, -8314, 2, 0, 2, 0, 14, 3797, -10, -4448, 4, 0, 0, 0, 13, 8991, -11, -6500, 2, 0, -3, 0, 13, 1941, 14, 4027, 0, 1, -2, 0, -9, -6791, -7, -27, 2, 0, -1, 2, -9, -3659, 0, 7740, 2, -1, -2, 0, 8, 6055, 10, 562, 1, 0, 1, 0, -8, -4531, 6, 3220, 2, -2, 0, 0, 8, 502, -9, -8845, 0, 1, 2, 0, -7, -6302, 5, 7509, 0, 2, 0, 0, -7, -4475, 1, 657, 2, -2, -1, 0, 7, 3712, -4, -9501, 2, 0, 1, -2, -6, -3832, 4, 1311, 2, 0, 0, 2, -5, -7416, 0, 0, 4, -1, -1, 0, 4, 3740, -3, -9580, 0, 0, 2, 2, -3, -9976, 0, 0, 3, 0, -1, 0, -3, -2097, 3, 2582, 2, 1, 1, 0, -2, -9145, 2, 6164, 4, -1, -2, 0, 2, 7319, -1, -8970, 0, 2, -1, 0, -2, -5679, -2, -1171, 2, 2, -1, 0, -2, -5212, 2, 3536, 2, 1, -2, 0, 2, 4889, 0, 1437, 2, -1, 0, -2, 2, 1461, 0, 6571, 4, 0, 1, 0, 1, 9777, -1, -4226, 0, 0, 4, 0, 1, 9337, -1, -1169, 4, -1, 0, 0, 1, 8708, -1, -5714, 1, 0, -2, 0, -1, -7530, -1, -7385, 2, 1, 0, -2, -1, -4372, 0, -1357, 0, 0, 2, -2, -1, -3726, -4, -4212, 1, 1, 1, 0, 1, 2618, 0, -9333, 3, 0, -2, 0, -1, -2241, 0, 8624, 4, 0, -3, 0, 1, 1868, 0, -5142, 2, -1, 2, 0, 1, 1770, 0, -8488, 0, 2, 1, 0, -1, -1617, 1, 1655, 1, 1, -1, 0, 1, 777, 0, 8512, 2, 0, 3, 0, 1, 595, 0, -6697, 2, 0, 1, 2, 0, -9902, 0, 0, 2, 0, -4, 0, 0, 9483, 0, 7785, 2, -2, 1, 0, 0, 7517, 0, -6575, 0, 1, -3, 0, 0, -6694, 0, -4224, 4, 1, -1, 0, 0, -6352, 0, 5788, 1, 0, 2, 0, 0, -5840, 0, 3785, 1, 0, 0, -2, 0, -5833, 0, -7956, 6, 0, -2, 0, 0, 5716, 0, -4225, 2, 0, -2, -2, 0, -5606, 0, 4726, 1, -1, 0, 0, 0, -5569, 0, 4976, 0, 1, 3, 0, 0, -5459, 0, 3551, 2, 0, -2, 2, 0, -5357, 0, 7740, 2, 0, -1, -2, 0, 1790, 8, 7516, 3, 0, 0, 0, 0, 4042, -1, -4189, 2, -1, -3, 0, 0, 4784, 0, 4950, 2, -1, 3, 0, 0, 932, 0, -585, 2, 0, 2, -2, 0, -4538, 0, 2840, 2, -1, -1, 2, 0, -4262, 0, 373, 0, 0, 0, 4, 0, 4203, 0, 0, 0, 1, 0, 2, 0, 4134, 0, -1580, 6, 0, -1, 0, 0, 3945, 0, -2866, 2, -1, 0, 2, 0, -3821, 0, 0, 2, -1, 1, -2, 0, -3745, 0, 2094, 4, 1, -2, 0, 0, -3576, 0, 2370, 1, 1, -2, 0, 0, 3497, 0, 3323, 2, -3, 0, 0, 0, 3398, 0, -4107, 0, 0, 3, 2, 0, -3286, 0, 0, 4, -2, -1, 0, 0, -3087, 0, -2790, 0, 1, -1, -2, 0, 3015, 0, 0, 4, 0, -1, -2, 0, 3009, 0, -3218, 2, -2, -2, 0, 0, 2942, 0, 3430, 6, 0, -3, 0, 0, 2925, 0, -1832, 2, 1, 2, 0, 0, -2902, 0, 2125, 4, 1, 0, 0, 0, -2891, 0, 2445, 4, -1, 1, 0, 0, 2825, 0, -2029, 3, 1, -1, 0, 0, 2737, 0, -2126, 0, 1, 1, 2, 0, 2634, 0, 0, 1, 0, 0, 2, 0, 2543, 0, 0, 3, 0, 0, -2, 0, -2530, 0, 2010, 2, 2, -2, 0, 0, -2499, 0, -1089, 2, -3, -1, 0, 0, 2469, 0, -1481, 3, -1, -1, 0, 0, -2314, 0, 2556, 4, 0, 2, 0, 0, 2185, 0, -1392, 4, 0, -1, 2, 0, -2013, 0, 0, 0, 2, -2, 0, 0, -1931, 0, 0, 2, 2, 0, 0, 0, -1858, 0, 0, 2, 1, -3, 0, 0, 1762, 0, 0, 4, 0, -2, 2, 0, -1698, 0, 0, 4, -2, -2, 0, 0, 1578, 0, -1083, 4, -2, 0, 0, 0, 1522, 0, -1281, 3, 1, 0, 0, 0, 1499, 0, -1077, 1, -1, -1, 0, 0, -1364, 0, 1141, 1, -3, 0, 0, 0, -1281, 0, 0, 6, 0, 0, 0, 0, 1261, 0, -859, 2, 0, 2, 2, 0, -1239, 0, 0, 1, -1, 1, 0, 0, -1207, 0, 1100, 0, 0, 5, 0, 0, 1110, 0, -589, 0, 3, 0, 0, 0, -1013, 0, 213, 4, -1, -3, 0, 0, 998, 0, 0}, a.j.AppCompatTheme_windowMinWidthMajor, 1, dArr19);
        a(new short[]{0, 0, 0, 1, 18461, 2387, 0, 0, 1, 1, 1010, 1671, 0, 0, 1, -1, 999, 6936, 2, 0, 0, -1, 623, 6524, 2, 0, -1, 1, 199, 4837, 2, 0, -1, -1, 166, 5741, 2, 0, 0, 1, 117, 2607, 0, 0, 2, 1, 61, 9120, 2, 0, 1, -1, 33, 3572, 0, 0, 2, -1, 31, 7597, 2, -1, 0, -1, 29, 5766, 2, 0, -2, -1, 15, 5663, 2, 0, 1, 1, 15, 1216, 2, 1, 0, -1, -12, -941, 2, -1, -1, 1, 8, 8681, 2, -1, 0, 1, 7, 9586, 2, -1, -1, -1, 7, 4346, 0, 1, -1, -1, -6, -7314, 4, 0, -1, -1, 6, 5796, 0, 1, 0, 1, -6, -4601, 0, 0, 0, 3, -6, -2965, 0, 1, -1, 1, -5, -6324, 1, 0, 0, 1, -5, -3684, 0, 1, 1, 1, -5, -3113, 0, 1, 1, -1, -5, -759, 0, 1, 0, -1, -4, -8396, 1, 0, 0, -1, -4, -8057, 0, 0, 3, 1, 3, 9841, 4, 0, 0, -1, 3, 6745, 4, 0, -1, 1, 2, 9985, 0, 0, 1, -3, 2, 7986, 4, 0, -2, 1, 2, 4139, 2, 0, 0, -3, 2, 1863, 2, 0, 2, -1, 2, 1462, 2, -1, 1, -1, 1, 7660, 2, 0, -2, 1, -1, -6244, 0, 0, 3, -1, 1, 5813, 2, 0, 2, 1, 1, 5198, 2, 0, -3, -1, 1, 5156, 2, 1, -1, 1, -1, -3178, 2, 1, 0, 1, -1, -2643, 4, 0, 0, 1, 1, 1919, 2, -1, 1, 1, 1, 1346, 2, -2, 0, -1, 1, 859, 0, 0, 1, 3, -1, -194, 2, 1, 1, -1, 0, -8227, 1, 1, 0, -1, 0, 8042, 1, 1, 0, 1, 0, 8026, 0, 1, -2, -1, 0, -7932, 2, 1, -1, -1, 0, -7910, 1, 0, 1, 1, 0, -6674, 2, -1, -2, -1, 0, 6502, 0, 1, 2, 1, 0, -6388, 4, 0, -2, -1, 0, 6337, 4, -1, -1, -1, 0, 5958, 1, 0, 1, -1, 0, -5889, 4, 0, 1, -1, 0, 4734, 1, 0, -1, -1, 0, -4299, 4, -1, 0, -1, 0, 4149, 2, -2, 0, 1, 0, 3835, 3, 0, 0, -1, 0, -3518, 4, -1, -1, 1, 0, 3388, 2, 0, -1, -3, 0, 3291, 2, -2, -1, 1, 0, 3147, 0, 1, 2, -1, 0, -3129, 3, 0, -1, -1, 0, -3052, 0, 1, -2, 1, 0, -3013, 2, 0, 1, -3, 0, -2912, 2, -2, -1, -1, 0, 2686, 0, 0, 4, 1, 0, 2633, 2, 0, -3, 1, 0, 2541, 2, 0, -1, 3, 0, -2448, 2, 1, 1, 1, 0, -2370, 4, -1, -2, 1, 0, 2138, 4, 0, 1, 1, 0, 2126, 3, 0, -1, 1, 0, -2059, 4, 1, -1, -1, 0, -1719}, 77, 3, this.p);
        double d85 = this.n;
        double d86 = this.L;
        double d87 = this.v;
        this.n = d85 + (((((((d86 * d87) + this.K) * d87) + this.J) * d87) + this.I) * d87 * 1.0E-5d);
        double[] dArr20 = this.p;
        dArr20[0] = this.q + this.n + (dArr20[0] * 1.0E-4d);
        dArr20[1] = (dArr20[1] * 1.0E-4d) + this.o;
        dArr20[2] = (dArr20[2] * 1.0E-4d) + 385000.52899d;
        dArr20[2] = dArr20[2] / 1.4959787066E8d;
        dArr20[0] = j * c(dArr20[0]);
        double[] dArr21 = this.p;
        dArr21[1] = j * dArr21[1];
        for (int i = 0; i < 3; i++) {
            dArr[i] = this.p[i];
        }
        return 0;
    }

    private int b(double d2, double[] dArr, int i, String str) {
        this.v = (d2 - 2451545.0d) / 36525.0d;
        double d3 = this.v;
        this.w = d3 * d3;
        double d4 = this.w;
        this.x = d3 * d4;
        this.y = d4 * d4;
        if (d2 >= 254900.5d && d2 <= 3697000.5d) {
            b();
            int i2 = i + 0;
            dArr[i2] = bc.a(((this.q - this.s) * j) + 3.141592653589793d);
            dArr[i + 1] = 0.0d;
            dArr[i + 2] = 0.002710625132447323d;
            double d5 = (this.q - this.u) * j;
            dArr[i2] = bc.a(dArr[i2] - d5);
            bc.b(dArr, i, dArr, i);
            bc.a(dArr, i, dArr, i, -0.08980410850026319d);
            bc.a(dArr, i, dArr, i);
            dArr[i2] = bc.a(dArr[i2] + d5);
            return 0;
        }
        if (str == "") {
            str = "";
        }
        String str2 = (((("jd " + d2) + " outside mean node apogee range ") + 254900.5d) + " .. ") + 3697000.5d;
        if (str.length() + str2.length() < 256) {
            StringBuilder sb = new StringBuilder();
            sb.append(str);
            sb.append(str2);
            return -1;
        }
        return -1;
    }

    private void b() {
        this.r = c(((Math.IEEEremainder(this.v, 1.0d) * 1.296E8d) - (this.v * 3418.961646d)) + 1287104.76154d);
        double d2 = this.r;
        double d3 = this.v;
        this.r = d2 + (((((((((((((((((1.62E-20d * d3) - 1.039E-17d) * d3) - 3.83508E-15d) * d3) + 4.237343E-13d) * d3) + 8.8555011E-11d) * d3) - 4.77258489E-8d) * d3) - 1.1297037031E-5d) * d3) + 1.4732069041E-4d) * d3) - 0.552891801772d) * this.w);
        this.u = c((d3 * 1.7395272630983E9d) + 335779.55755d);
        this.s = c((this.v * 1.7179159234728E9d) + 485868.28096d);
        this.t = c((this.v * 1.6029616014603E9d) + 1072260.73512d);
        this.q = c((this.v * 1.73256437283264E9d) + 785939.95571d);
        double d4 = this.u;
        double[] dArr = m;
        double d5 = dArr[5];
        double d6 = this.v;
        double d7 = (((((((((d5 * d6) + dArr[4]) * d6) + dArr[3]) * d6) + dArr[2]) * d6) + dArr[1]) * d6) + dArr[0];
        double d8 = this.w;
        this.u = d4 + (d7 * d8);
        this.s += ((((((((((dArr[11] * d6) + dArr[10]) * d6) + dArr[9]) * d6) + dArr[8]) * d6) + dArr[7]) * d6) + dArr[6]) * d8;
        this.t += ((((((((((dArr[17] * d6) + dArr[16]) * d6) + dArr[15]) * d6) + dArr[14]) * d6) + dArr[13]) * d6) + dArr[12]) * d8;
        this.q += ((((((((((dArr[23] * d6) + dArr[22]) * d6) + dArr[21]) * d6) + dArr[20]) * d6) + dArr[19]) * d6) + dArr[18]) * d8;
    }

    private static void b(double[] dArr, double[] dArr2, long j2) {
        double[] dArr3 = new double[6];
        double[] dArr4 = new double[6];
        double[] dArr5 = new double[6];
        double[] dArr6 = new double[6];
        for (int i = 0; i <= 5; i++) {
            double d2 = dArr[i];
            dArr3[i] = d2;
            dArr5[i] = d2;
        }
        double sqrt = Math.sqrt(a(dArr5, 0));
        for (int i2 = 0; i2 <= 2; i2++) {
            dArr4[i2] = (((dArr2[i2 + 3] / 24.0d) / 3600.0d) / 2.99792458E8d) * 1.4959787066E11d;
        }
        double sqrt2 = Math.sqrt(1.0d - a(dArr4, 0));
        double a2 = a(dArr5, dArr4, 0) / sqrt;
        double d3 = sqrt2 + 1.0d;
        double d4 = (a2 / d3) + 1.0d;
        for (int i3 = 0; i3 <= 2; i3++) {
            dArr[i3] = ((dArr[i3] * sqrt2) + ((d4 * sqrt) * dArr4[i3])) / (a2 + 1.0d);
        }
        if ((j2 & 256) != 0) {
            for (int i4 = 0; i4 <= 2; i4++) {
                dArr5[i4] = dArr3[i4] - (dArr3[i4 + 3] * 1.0E-4d);
            }
            double sqrt3 = Math.sqrt(a(dArr5, 0));
            double a3 = a(dArr5, dArr4, 0) / sqrt3;
            double d5 = (a3 / d3) + 1.0d;
            for (int i5 = 0; i5 <= 2; i5++) {
                dArr6[i5] = ((dArr5[i5] * sqrt2) + ((d5 * sqrt3) * dArr4[i5])) / (a3 + 1.0d);
            }
            for (int i6 = 0; i6 <= 2; i6++) {
                int i7 = i6 + 3;
                dArr[i7] = dArr[i7] + (((dArr[i6] - dArr3[i6]) - (dArr6[i6] - dArr5[i6])) / 1.0E-4d);
            }
        }
    }

    private static double c(double d2) {
        return d2 - (Math.floor(d2 / 1296000.0d) * 1296000.0d);
    }

    private void c(double d2, double[] dArr) {
        bc.b(dArr, 0, dArr, 0);
        bc.a(dArr, 0, dArr, 0, -this.f675a.g.c, this.f675a.g.d);
        bc.a(dArr, 0, d2, 1);
    }

    public final double a(double d2) {
        double[] dArr = new double[6];
        bd.f fVar = this.f675a.m;
        if (!this.f675a.b) {
            a(0);
        }
        dArr[0] = 1.0d;
        dArr[2] = 0.0d;
        dArr[1] = 0.0d;
        if (d2 != 2451545.0d) {
            bc.a(dArr, 0, d2, 1);
        }
        bc.a(dArr, 0, fVar.c, -1);
        bc.a(dArr, 0, dArr, 0, bc.d(fVar.c));
        bc.a(dArr, 0, dArr, 0);
        dArr[0] = (dArr[0] * 57.2957795130823d) - fVar.b;
        return bc.c(-dArr[0]);
    }

    /* JADX WARN: Removed duplicated region for block: B:301:0x0712 A[LOOP:15: B:300:0x0710->B:301:0x0712, LOOP_END] */
    /* JADX WARN: Removed duplicated region for block: B:305:0x0723  */
    /* JADX WARN: Removed duplicated region for block: B:310:0x072d  */
    /*
        Code decompiled incorrectly, please refer to instructions dump.
        To view partially-correct add '--show-bad-code' argument
    */
    public final int a(double r34, int r36, double[] r37) {
        /*
            Method dump skipped, instructions count: 1897
            To view this dump add '--comments-level debug' option
        */
        throw new UnsupportedOperationException("Method not decompiled: enc.icssoftwares.com.vakkiampro.be.a(double, int, double[]):int");
    }

    public final void a(int i) {
        double d2;
        double[] dArr = {2433282.5d, 2415020.0d, 2415020.0d, 2415020.0d, 2415020.0d, 2415020.0d, 2415020.0d, 2415020.0d, 2415020.0d, 1684532.5d, 1684532.5d, 1684532.5d, 1684532.5d, 1673941.0d, 1684532.5d, 1674484.0d, 1927135.8747793d, 1746443.513d, 2451545.0d, 2415020.0d, 2433282.42345905d};
        double[] dArr2 = {24.042044444d, 22.460469999999987d, 26.41305d, 21.01443999999998d, 18.66095999999999d, 22.363888999999972d, 26.963097600000026d, 21.082222d, 21.365556000000026d, -3.36667d, -4.76667d, -5.61667d, -4.56667d, -5.079167d, -4.44088389d, -9.33333d, 0.0d, 0.0d, 0.0d, 0.0d, 0.0d};
        bd.f fVar = this.f675a.m;
        fVar.f681a = i;
        if (i >= 256) {
            i %= 256;
        }
        if (i == 18 || i == 19 || i == 20) {
            fVar.f681a = 256 | fVar.f681a;
        }
        if (i >= 21 && i != 255) {
            i = 0;
            fVar.f681a = 0;
        }
        this.f675a.b = true;
        if (i == 255) {
            d2 = 0.0d;
            fVar.c = 0.0d;
        } else {
            fVar.c = dArr[i];
            d2 = dArr2[i];
        }
        fVar.b = d2;
        a();
    }
}
