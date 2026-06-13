package enc.icssoftwares.com.vakkiampro;

import android.content.Context;
import java.util.Date;
/* loaded from: classes.dex */
public final class l {
    Context j;
    private long k;

    /* renamed from: a  reason: collision with root package name */
    public double f695a = 0.0d;
    public double b = 0.0d;
    public double c = 0.0d;
    public double d = 0.0d;
    public double e = 0.0d;
    public double f = 0.0d;
    public double g = 0.0d;
    public double h = 0.0d;
    public double i = 0.0d;
    private Date l = new Date();
    private Date m = new Date();

    public final void a() {
        long abs;
        long abs2;
        k kVar = new k(this.j);
        String g = kVar.g(this.l);
        s sVar = new s();
        String[] split = g.split("-");
        sVar.f704a = Integer.valueOf(split[1]).intValue();
        sVar.b = Integer.valueOf(split[2]).intValue();
        sVar.c = Integer.valueOf(split[3]).intValue();
        long j = (((sVar.f704a * 60) + sVar.b) * 60) + sVar.c;
        String[] split2 = kVar.g(this.m).split("-");
        sVar.f704a = Integer.valueOf(split2[1]).intValue();
        sVar.b = Integer.valueOf(split2[2]).intValue();
        sVar.c = Integer.valueOf(split2[3]).intValue();
        long j2 = (((sVar.f704a * 60) + sVar.b) * 60) + sVar.c;
        sVar.e = false;
        if (j > j2) {
            sVar.e = true;
        }
        long abs3 = Math.abs(j - j2);
        if (abs3 > 180000) {
            sVar.e = true ^ sVar.e;
            if (sVar.e) {
                abs = 1296000 - Math.abs(j2);
                abs2 = Math.abs(j);
            } else {
                abs = 1296000 - Math.abs(j);
                abs2 = Math.abs(j2);
            }
            abs3 = abs + abs2;
        }
        double d = (abs3 / 3600.0d) * this.k;
        double d2 = sVar.e ? j - d : j + d;
        if (d2 < 0.0d) {
            d2 += 1296000.0d;
        }
        this.f695a = d2;
        this.f695a /= 3600.0d;
        double d3 = this.f695a;
        if (d3 >= 360.0d) {
            this.f695a = d3 - 360.0d;
        }
        System.out.println("VSun=" + this.f695a);
        sVar.d = 0;
        sVar.c = (int) (d2 % 60.0d);
        double d4 = d2 / 60.0d;
        sVar.b = (int) (d4 % 60.0d);
        sVar.f704a = (int) (d4 / 60.0d);
        if (sVar.f704a >= 360) {
            sVar.f704a -= 360;
        }
    }

    public final void a(Context context, Date date, long j) {
        this.l = date;
        Date date2 = new Date();
        date2.setTime(this.l.getTime() + 86400000);
        this.m = date2;
        this.j = context;
        this.k = j;
    }

    public final void b() {
        long abs;
        long abs2;
        k kVar = new k(this.j);
        String f = kVar.f(this.l);
        s sVar = new s();
        String[] split = f.split("-");
        sVar.f704a = Integer.valueOf(split[1]).intValue();
        sVar.b = Integer.valueOf(split[2]).intValue();
        sVar.c = Integer.valueOf(split[3]).intValue();
        long j = (((sVar.f704a * 60) + sVar.b) * 60) + sVar.c;
        String[] split2 = kVar.f(this.m).split("-");
        sVar.f704a = Integer.valueOf(split2[1]).intValue();
        sVar.b = Integer.valueOf(split2[2]).intValue();
        sVar.c = Integer.valueOf(split2[3]).intValue();
        long j2 = (((sVar.f704a * 60) + sVar.b) * 60) + sVar.c;
        sVar.e = false;
        if (j > j2) {
            sVar.e = true;
        }
        long abs3 = Math.abs(j - j2);
        if (abs3 > 180000) {
            sVar.e = true ^ sVar.e;
            if (sVar.e) {
                abs = 1296000 - Math.abs(j2);
                abs2 = Math.abs(j);
            } else {
                abs = 1296000 - Math.abs(j);
                abs2 = Math.abs(j2);
            }
            abs3 = abs + abs2;
        }
        double d = (abs3 / 3600.0d) * this.k;
        double d2 = sVar.e ? j - d : j + d;
        if (d2 < 0.0d) {
            d2 += 1296000.0d;
        }
        this.b = d2;
        this.b /= 3600.0d;
        double d3 = this.b;
        if (d3 >= 360.0d) {
            this.b = d3 - 360.0d;
        }
        System.out.println("VMoon=" + this.b);
        sVar.d = 0;
        sVar.c = (int) (d2 % 60.0d);
        double d4 = d2 / 60.0d;
        sVar.b = (int) (d4 % 60.0d);
        sVar.f704a = (int) (d4 / 60.0d);
        if (sVar.f704a >= 360) {
            sVar.f704a -= 360;
        }
    }

    public final void c() {
        long abs;
        long abs2;
        k kVar = new k(this.j);
        String a2 = kVar.a(this.l);
        s sVar = new s();
        String[] split = a2.split("-");
        sVar.f704a = Integer.valueOf(split[1]).intValue();
        sVar.b = Integer.valueOf(split[2]).intValue();
        sVar.c = Integer.valueOf(split[3]).intValue();
        long j = (((sVar.f704a * 60) + sVar.b) * 60) + sVar.c;
        String[] split2 = kVar.a(this.m).split("-");
        sVar.f704a = Integer.valueOf(split2[1]).intValue();
        sVar.b = Integer.valueOf(split2[2]).intValue();
        sVar.c = Integer.valueOf(split2[3]).intValue();
        long j2 = (((sVar.f704a * 60) + sVar.b) * 60) + sVar.c;
        sVar.e = false;
        if (j > j2) {
            sVar.e = true;
        }
        long abs3 = Math.abs(j - j2);
        if (abs3 > 180000) {
            sVar.e = true ^ sVar.e;
            if (sVar.e) {
                abs = 1296000 - Math.abs(j2);
                abs2 = Math.abs(j);
            } else {
                abs = 1296000 - Math.abs(j);
                abs2 = Math.abs(j2);
            }
            abs3 = abs + abs2;
        }
        double d = (abs3 / 3600.0d) * this.k;
        double d2 = sVar.e ? j - d : j + d;
        if (d2 < 0.0d) {
            d2 += 1296000.0d;
        }
        if (sVar.e) {
            this.c = (-1.0d) * d2;
        } else {
            this.c = d2;
        }
        this.c /= 3600.0d;
        double d3 = this.c;
        if (d3 >= 360.0d) {
            this.c = d3 - 360.0d;
        }
        System.out.println("VMars=" + this.c);
        sVar.d = 0;
        sVar.c = (int) (d2 % 60.0d);
        double d4 = d2 / 60.0d;
        sVar.b = (int) (d4 % 60.0d);
        sVar.f704a = (int) (d4 / 60.0d);
        if (sVar.f704a >= 360) {
            sVar.f704a -= 360;
        }
    }

    public final void d() {
        long abs;
        long abs2;
        k kVar = new k(this.j);
        String h = kVar.h(this.l);
        System.out.println("RecStrMercury1=".concat(String.valueOf(h)));
        s sVar = new s();
        String[] split = h.split("-");
        sVar.f704a = Integer.valueOf(split[1]).intValue();
        sVar.b = Integer.valueOf(split[2]).intValue();
        sVar.c = Integer.valueOf(split[3]).intValue();
        long j = (((sVar.f704a * 60) + sVar.b) * 60) + sVar.c;
        String h2 = kVar.h(this.m);
        System.out.println("RecStrMercury2=".concat(String.valueOf(h2)));
        String[] split2 = h2.split("-");
        sVar.f704a = Integer.valueOf(split2[1]).intValue();
        sVar.b = Integer.valueOf(split2[2]).intValue();
        sVar.c = Integer.valueOf(split2[3]).intValue();
        long j2 = (((sVar.f704a * 60) + sVar.b) * 60) + sVar.c;
        sVar.e = false;
        if (j > j2) {
            sVar.e = true;
        }
        long abs3 = Math.abs(j - j2);
        if (abs3 > 180000) {
            sVar.e = true ^ sVar.e;
            if (sVar.e) {
                abs = 1296000 - Math.abs(j2);
                abs2 = Math.abs(j);
            } else {
                abs = 1296000 - Math.abs(j);
                abs2 = Math.abs(j2);
            }
            abs3 = abs + abs2;
        }
        double d = (abs3 / 3600.0d) * this.k;
        double d2 = sVar.e ? j - d : j + d;
        if (d2 < 0.0d) {
            d2 += 1296000.0d;
        }
        if (sVar.e) {
            this.d = (-1.0d) * d2;
        } else {
            this.d = d2;
        }
        this.d /= 3600.0d;
        double d3 = this.d;
        if (d3 >= 360.0d) {
            this.d = d3 - 360.0d;
        }
        System.out.println("VMercury=" + this.d);
        sVar.d = 0;
        sVar.c = (int) (d2 % 60.0d);
        double d4 = d2 / 60.0d;
        sVar.b = (int) (d4 % 60.0d);
        sVar.f704a = (int) (d4 / 60.0d);
        if (sVar.f704a >= 360) {
            sVar.f704a -= 360;
        }
    }

    public final void e() {
        long abs;
        long abs2;
        k kVar = new k(this.j);
        String b = kVar.b(this.l);
        s sVar = new s();
        String[] split = b.split("-");
        sVar.f704a = Integer.valueOf(split[1]).intValue();
        sVar.b = Integer.valueOf(split[2]).intValue();
        sVar.c = Integer.valueOf(split[3]).intValue();
        long j = (((sVar.f704a * 60) + sVar.b) * 60) + sVar.c;
        String[] split2 = kVar.b(this.m).split("-");
        sVar.f704a = Integer.valueOf(split2[1]).intValue();
        sVar.b = Integer.valueOf(split2[2]).intValue();
        sVar.c = Integer.valueOf(split2[3]).intValue();
        long j2 = (((sVar.f704a * 60) + sVar.b) * 60) + sVar.c;
        sVar.e = false;
        if (j > j2) {
            sVar.e = true;
        }
        long abs3 = Math.abs(j - j2);
        if (abs3 > 180000) {
            sVar.e = true ^ sVar.e;
            if (sVar.e) {
                abs = 1296000 - Math.abs(j2);
                abs2 = Math.abs(j);
            } else {
                abs = 1296000 - Math.abs(j);
                abs2 = Math.abs(j2);
            }
            abs3 = abs + abs2;
        }
        double d = (abs3 / 3600.0d) * this.k;
        double d2 = sVar.e ? j - d : j + d;
        if (d2 < 0.0d) {
            d2 += 1296000.0d;
        }
        if (sVar.e) {
            this.e = (-1.0d) * d2;
        } else {
            this.e = d2;
        }
        this.e /= 3600.0d;
        double d3 = this.e;
        if (d3 >= 360.0d) {
            this.e = d3 - 360.0d;
        }
        System.out.println("VJupiter=" + this.e);
        sVar.d = 0;
        sVar.c = (int) (d2 % 60.0d);
        double d4 = d2 / 60.0d;
        sVar.b = (int) (d4 % 60.0d);
        sVar.f704a = (int) (d4 / 60.0d);
        if (sVar.f704a >= 360) {
            sVar.f704a -= 360;
        }
    }

    public final void f() {
        long abs;
        long abs2;
        k kVar = new k(this.j);
        String c = kVar.c(this.l);
        s sVar = new s();
        String[] split = c.split("-");
        sVar.f704a = Integer.valueOf(split[1]).intValue();
        sVar.b = Integer.valueOf(split[2]).intValue();
        sVar.c = Integer.valueOf(split[3]).intValue();
        long j = (((sVar.f704a * 60) + sVar.b) * 60) + sVar.c;
        String[] split2 = kVar.c(this.m).split("-");
        sVar.f704a = Integer.valueOf(split2[1]).intValue();
        sVar.b = Integer.valueOf(split2[2]).intValue();
        sVar.c = Integer.valueOf(split2[3]).intValue();
        long j2 = (((sVar.f704a * 60) + sVar.b) * 60) + sVar.c;
        sVar.e = false;
        if (j > j2) {
            sVar.e = true;
        }
        long abs3 = Math.abs(j - j2);
        if (abs3 > 180000) {
            sVar.e = true ^ sVar.e;
            if (sVar.e) {
                abs = 1296000 - Math.abs(j2);
                abs2 = Math.abs(j);
            } else {
                abs = 1296000 - Math.abs(j);
                abs2 = Math.abs(j2);
            }
            abs3 = abs + abs2;
        }
        double d = (abs3 / 3600.0d) * this.k;
        double d2 = sVar.e ? j - d : j + d;
        if (d2 < 0.0d) {
            d2 += 1296000.0d;
        }
        if (sVar.e) {
            this.f = (-1.0d) * d2;
        } else {
            this.f = d2;
        }
        this.f /= 3600.0d;
        double d3 = this.f;
        if (d3 >= 360.0d) {
            this.f = d3 - 360.0d;
        }
        System.out.println("VVenus=" + this.f);
        sVar.d = 0;
        sVar.c = (int) (d2 % 60.0d);
        double d4 = d2 / 60.0d;
        sVar.b = (int) (d4 % 60.0d);
        sVar.f704a = (int) (d4 / 60.0d);
        if (sVar.f704a >= 360) {
            sVar.f704a -= 360;
        }
    }

    public final void g() {
        long abs;
        long abs2;
        k kVar = new k(this.j);
        String d = kVar.d(this.l);
        s sVar = new s();
        String[] split = d.split("-");
        sVar.f704a = Integer.valueOf(split[1]).intValue();
        sVar.b = Integer.valueOf(split[2]).intValue();
        sVar.c = Integer.valueOf(split[3]).intValue();
        long j = (((sVar.f704a * 60) + sVar.b) * 60) + sVar.c;
        String[] split2 = kVar.d(this.m).split("-");
        sVar.f704a = Integer.valueOf(split2[1]).intValue();
        sVar.b = Integer.valueOf(split2[2]).intValue();
        sVar.c = Integer.valueOf(split2[3]).intValue();
        long j2 = (((sVar.f704a * 60) + sVar.b) * 60) + sVar.c;
        sVar.e = false;
        if (j > j2) {
            sVar.e = true;
        }
        long abs3 = Math.abs(j - j2);
        if (abs3 > 180000) {
            sVar.e = true ^ sVar.e;
            if (sVar.e) {
                abs = 1296000 - Math.abs(j2);
                abs2 = Math.abs(j);
            } else {
                abs = 1296000 - Math.abs(j);
                abs2 = Math.abs(j2);
            }
            abs3 = abs + abs2;
        }
        double d2 = (abs3 / 3600.0d) * this.k;
        double d3 = sVar.e ? j - d2 : j + d2;
        if (d3 < 0.0d) {
            d3 += 1296000.0d;
        }
        if (sVar.e) {
            this.g = (-1.0d) * d3;
        } else {
            this.g = d3;
        }
        this.g /= 3600.0d;
        double d4 = this.g;
        if (d4 >= 360.0d) {
            this.g = d4 - 360.0d;
        }
        System.out.println("VSaturn=" + this.g);
        sVar.d = 0;
        sVar.c = (int) (d3 % 60.0d);
        double d5 = d3 / 60.0d;
        sVar.b = (int) (d5 % 60.0d);
        sVar.f704a = (int) (d5 / 60.0d);
        if (sVar.f704a >= 360) {
            sVar.f704a -= 360;
        }
    }

    public final void h() {
        long abs;
        long abs2;
        k kVar = new k(this.j);
        String e = kVar.e(this.l);
        s sVar = new s();
        String[] split = e.split("-");
        sVar.f704a = Integer.valueOf(split[1]).intValue();
        sVar.b = Integer.valueOf(split[2]).intValue();
        sVar.c = Integer.valueOf(split[3]).intValue();
        long j = (((sVar.f704a * 60) + sVar.b) * 60) + sVar.c;
        String[] split2 = kVar.e(this.m).split("-");
        sVar.f704a = Integer.valueOf(split2[1]).intValue();
        sVar.b = Integer.valueOf(split2[2]).intValue();
        sVar.c = Integer.valueOf(split2[3]).intValue();
        long j2 = (((sVar.f704a * 60) + sVar.b) * 60) + sVar.c;
        sVar.e = false;
        if (j > j2) {
            sVar.e = true;
        }
        long abs3 = Math.abs(j - j2);
        if (abs3 > 180000) {
            sVar.e = true ^ sVar.e;
            if (sVar.e) {
                abs = 1296000 - Math.abs(j2);
                abs2 = Math.abs(j);
            } else {
                abs = 1296000 - Math.abs(j);
                abs2 = Math.abs(j2);
            }
            abs3 = abs + abs2;
        }
        double d = (abs3 / 3600.0d) * this.k;
        double d2 = sVar.e ? j - d : j + d;
        if (d2 < 0.0d) {
            d2 += 1296000.0d;
        }
        this.h = d2;
        this.h /= 3600.0d;
        double d3 = this.h;
        if (d3 >= 360.0d) {
            this.h = d3 - 360.0d;
        }
        System.out.println("VRahu=" + this.h);
        sVar.d = 0;
        sVar.c = (int) (d2 % 60.0d);
        double d4 = d2 / 60.0d;
        sVar.b = (int) (d4 % 60.0d);
        sVar.f704a = (int) (d4 / 60.0d);
        if (sVar.f704a >= 360) {
            sVar.f704a -= 360;
        }
    }
}
