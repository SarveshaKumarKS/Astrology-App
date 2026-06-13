import java.io.*;
import java.nio.file.*;
import java.util.*;

/**
 * Standalone Vakya computation engine — faithful Java port of ICS Vakkiam Pro
 * classes k.java + l.java, with Android Context replaced by plain file I/O.
 *
 * Usage:
 *   java VakkiamEngine <vakya_data_dir>
 * Stdin: lines of "idx|YYYY|MM|DD|HH|MM"
 * Stdout: "idx|Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn|Rahu|Ketu"
 *         (all decimal degrees, 6 decimal places)
 *
 * LAT=11.6643, LON=78.185 (Salem, India), TZ=5.5h are hard-wired for the
 * 729 test cases but can be overridden per-line as a 7th pipe field.
 */
public class VakkiamEngine {

    // ── Tamil month cumulative day-offsets from Tamil New Year ──────────────
    // Source: k.java a(int i) — sVarArr[0..12].{f704a,b,c,d}
    static final int[][] SAKA_MONTHS = {
        {  0,  0,  0,  0},   // Month 1  Chittirai
        { 30, 55, 32,  0},   // Month 2  Vaikasi
        { 62, 19, 44,  0},   // Month 3  Aani
        { 93, 56, 22,  0},   // Month 4  Aadi
        {125, 24, 34,  0},   // Month 5  Aavani
        {156, 26, 44,  0},   // Month 6  Purattasi
        {186, 54,  6,  0},   // Month 7  Aippasi
        {216, 48, 13,  0},   // Month 8  Karthigai
        {246, 18, 37,  0},   // Month 9  Margazhi
        {275, 39, 30,  0},   // Month 10 Thai
        {305,  6, 46,  0},   // Month 11 Maasi
        {334, 55, 10,  0},   // Month 12 Panguni
        {365, 15, 31, 15},   // Month 13 sentinel
    };

    // k.java a(long j): incremental SOLAR_MONTH_PARAMS[1..12]
    static final int[][] SOLAR_MONTH_PARAMS = {
        {1, 15, 31, 15},   // [0] sentinel / TNY
        {2, 55, 32,  0},   // [1] Vaikasi
        {6, 19, 44,  0},   // [2] Aani
        {2, 56, 22,  0},   // [3] Aadi
        {6, 24, 34,  0},   // [4] Aavani
        {2, 26, 44,  0},   // [5] Purattasi
        {4, 54,  6,  0},   // [6] Aippasi
        {6, 48, 13,  0},   // [7] Karthigai
        {1, 18, 37,  0},   // [8] Margazhi
        {2, 39, 30,  0},   // [9] Thai
        {4,  6, 46,  0},   // [10] Maasi
        {5, 55, 10,  0},   // [11] Panguni
        {1, 15, 31, 15},   // [12] sentinel
    };

    // Threshold (gh,vi) for weekday-bump test
    static final int[][] SOLAR_THRESH = {
        {30,36},{31,16},{31,34},{31,24},{30,50},{30, 7},
        {29,24},{28,45},{28,26},{28,36},{29, 8},{29,52},{30,36},
    };

    // k.java FRIDAY=0 convention
    static final String[] WEEKDAYS = {
        "FRIDAY","SATURDAY","SUNDAY","MONDAY","TUESDAY","WEDNESDAY","THURSDAY"
    };
    // Java Calendar.DAY_OF_WEEK: 1=Sunday, 2=Monday, ..., 7=Saturday
    // Map: (DAY_OF_WEEK - 1) → Vakya weekday name
    static final String[] PY_TO_VAKYA = {
        "SUNDAY","MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY","SATURDAY"
    };

    // ── Sun manda correction tables ─────────────────────────────────────────
    static final int[] SUN_MANDA = {
        0, 14, 32, 54, 78, 105, 133, 163, 194, 224, 254, 284, 311, 335, 358,
        376, 391, 403, 411, 415, 416, 412, 406, 398, 386, 374, 361, 347, 334,
        322, 311, 303, 297, 295, 296, 301, 309, 322,
    };
    static final int[] SUN_MANDA_GRAD = {
        84, 108, 132, 144, 162, 168, 180, 186, 180, 180, 180, 162, 144, 138,
        108, 90, 72, 48, 24, 6, -24, -36, -48, -72, -72, -78, -84, -78, -72,
        -66, -48, -36, -12, 6, 30, 48, 78,
    };

    // Sun daily arc table — arcseconds per Tamil day
    static final int[] SUN_DAILY_ARCSEC = {
        3516, 3492, 3468, 3456, 3438, 3432, 3420, 3414, 3420, 3420, 3420, 3438,
        3456, 3462, 3492, 3510, 3528, 3552, 3576, 3594, 3624, 3636, 3648, 3672,
        3672, 3678, 3684, 3678, 3672, 3666, 3648, 3636, 3612, 3594, 3570, 3552, 3522,
    };

    // ── Moon khanda tables ──────────────────────────────────────────────────
    static final long[] MOON_KHANDAS = {
        1811308L, 1774192L, 1600984L, 1237200L, 1113480L,  989760L,  866040L,  742320L,
         618600L,  494880L,  371160L,  247440L,  123720L,  111348L,   98976L,   86604L,
          74232L,   61860L,   49488L,   37116L,   24744L,   12372L,   12124L,    9093L,
           6062L,    3031L,    2976L,    2728L,    2480L,    2232L,    1984L,    1736L,
           1488L,    1240L,     992L,     744L,     496L,     248L,
    };
    static final long[] MOON_ANCHORS = {
         844737L,  220467L,  763207L,  937000L,  584100L,  231200L, 1174300L,  821400L,
         468500L,  115600L, 1058700L,  705800L,  352900L,  576810L,  800720L, 1024630L,
        1248540L,  176450L,  400360L,  624270L,  848180L, 1072090L,  972244L, 1053183L,
        1134122L, 1215061L, 1198152L, 1098306L,  998460L,  898614L,  798768L,  698922L,
         599076L,  499230L,  399384L,  299538L,  199692L,   99846L,
    };

    // ── Rahu constants ──────────────────────────────────────────────────────
    static final long RAHU_KY_OFFSET   = 1600066L;
    static final long RAHU_PERIOD      = 6792L;
    static final long RAHU_SUBCYCLE    = 566L;
    static final long RAHU_MACRO       = 5654L;
    static final long RAHU_BIJA_ARCSEC = 300L;
    static final double[] RAHU_SPEED_INC = {
        12000.0, 6000.0, 3000.0, 1500.0, 750.0, 375.0, 187.5, 93.75,
        46.88, 23.44, 11.72, 5.86, 2.93, 1.46, 0.73, 0.37, 0.18
    };
    static final double[] RAHU_SPEED_LIMIT = {
        225632.0, 112816.0, 56408.0, 28204.0, 14102.0, 7051.0, 3525.5,
        1762.75, 881.38, 440.69, 220.34, 110.17, 55.09,
        27.54, 13.77, 6.89, 3.44
    };

    static final long FULL_CIRCLE = 1296000L;  // 360 * 3600 arcsec

    // ── Planet descriptors (Mars, Jupiter, Venus, Saturn, Mercury) ──────────
    static class PlanetDesc {
        String name;
        long[] khandas;
        int[]  gh;
        int[]  bija;
        long   period;
        int    rows;
        int    split;
        String fileLow, fileHigh;
        Integer cycleMod;
        int    col;
        boolean strict;  // Saturn uses > instead of >=
        int[] special;   // (deg, min, vi) fallback for day==0

        PlanetDesc(String n, long[] k, int[] g, int[] b, long period, int rows,
                   int split, String fl, String fh, Integer cm, int col,
                   boolean strict, int[] sp) {
            this.name=n; this.khandas=k; this.gh=g; this.bija=b;
            this.period=period; this.rows=rows; this.split=split;
            this.fileLow=fl; this.fileHigh=fh; this.cycleMod=cm;
            this.col=col; this.strict=strict; this.special=sp;
        }
    }

    static final PlanetDesc[] PLANETS = {
        new PlanetDesc("Mars",
            new long[]{1552827,634089,132589,28857,17158,11699},
            new int[]{35,9,21,41,37,4},
            new int[]{-402,5,27,133,-504,638},
            780, 39, 468, "arp.txt","pys.txt", null, 4, false,
            new int[]{118,0,-6}),
        new PlanetDesc("Jupiter",
            new long[]{1570425,974875,125648,65018,30315,21539,4387},
            new int[]{17,26,50,17,17,48,44},
            new int[]{-261,1,-9,133,-71,-619,274},
            399, 22, 168, "boi.txt","cip.txt", null, 4, false,
            new int[]{180,0,-4}),
        new PlanetDesc("Venus",
            new long[]{1561937,437945,174594,88756,44962,2919},
            new int[]{44,0,7,53,22,38},
            new int[]{18,0,28,-57,2102,-144},
            584, 40, 63, "goa.txt","dlf.txt", null, 5, false,
            new int[]{93,0,-1}),
        new PlanetDesc("Saturn",
            new long[]{1589474,570534,182994,21551,10964},
            new int[]{28,8,23,0,32},
            new int[]{-326,5,-13,43,401},
            378, 20, 190, "tcm.txt","htc.txt", 29, 4, true,
            new int[]{236,0,-6}),
        new PlanetDesc("Mercury",
            new long[]{1592740,16801,4750,2549},
            new int[]{22,54,53,15},
            new int[]{-33,-1,149,-446},
            116, 25, 223, "rap.txt","qnl.txt", null, 4, false,
            new int[]{240,0,-3}),
    };

    // ── Table storage ───────────────────────────────────────────────────────
    // Map: filename -> (rowNum -> double[])  preserves fractional bija columns
    private Map<String, Map<Integer, double[]>> tables = new HashMap<>();

    // Cache: year -> month_starts (14 Calendar objects: [0]=TNY, [1..12])
    private Map<Integer, Calendar[]> monthStartsCache = new HashMap<>();

    // ── Data directory ──────────────────────────────────────────────────────
    private String dataDir;

    public VakkiamEngine(String dataDir) throws IOException {
        this.dataDir = dataDir;
        loadAll();
    }

    // ── File loading ────────────────────────────────────────────────────────

    private void loadAll() throws IOException {
        String[] files = {
            "arp.txt","pys.txt","boi.txt","cip.txt","goa.txt","dlf.txt",
            "tcm.txt","htc.txt","rap.txt","qnl.txt","sre.txt","hsg.txt"
        };
        for (String fname : files) {
            File f = new File(dataDir, fname);
            if (f.exists()) {
                tables.put(fname, parseFile(f));
            }
        }
    }

    private Map<Integer, double[]> parseFile(File f) throws IOException {
        Map<Integer, double[]> result = new LinkedHashMap<>();
        try (BufferedReader br = new BufferedReader(new FileReader(f))) {
            String line;
            while ((line = br.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty() || !line.contains("=")) continue;
                int eq = line.indexOf('=');
                String key = line.substring(0, eq);
                String val = line.substring(eq + 1);
                int rowNum = Integer.parseInt(key.substring(1));
                String[] parts = val.split(",");
                double[] parsed = new double[parts.length];
                for (int i = 0; i < parts.length; i++) {
                    String p = parts[i].trim().replaceAll("[^0-9.\\-]", "");
                    if (p.isEmpty() || p.equals("-")) { parsed[i] = 0; continue; }
                    try {
                        parsed[i] = Double.parseDouble(p);
                    } catch (NumberFormatException ex) {
                        parsed[i] = 0;
                    }
                }
                result.put(rowNum, parsed);
            }
        }
        return result;
    }

    double[] getRow(String fname, int seq) {
        Map<Integer, double[]> tbl = tables.get(fname);
        if (tbl == null) return null;
        return tbl.get(seq);
    }

    // ── KY calendar arithmetic ──────────────────────────────────────────────
    // Faithful port of k.java a(long j) — the KY year arithmetic that produces
    // (C, D, E, F) = total days / ghatika / vinadi / prati at Tamil New Year.

    long[] kyYearArithmetic(int year) {
        long v = year + 3101L;
        long C = 365L * v;
        long D = 15L  * v;
        long E = 31L  * v;
        long F = 15L  * v;
        // carry E,F
        E += F / 60; F = F % 60;
        D += E / 60; E = E % 60;
        C += D / 60; D = D % 60;
        F -= 15;
        if (F < 0) { F += 60; E--; }
        E -= 51;
        if (E < 0) { E += 60; D--; }
        D -= 8;
        if (D < 0) { D += 60; C--; }
        C -= 2;
        return new long[]{C, D, E, F};
    }

    // Find Tamil New Year date for given Gregorian year
    Calendar findTamilNewYear(int year) {
        long[] cdefs = kyYearArithmetic(year);
        long C = cdefs[0], D = cdefs[1], E = cdefs[2];
        long dayCount = C + (D * 60 + E >= 1815 ? 1 : 0);
        String kyWkday = WEEKDAYS[(int)(dayCount % 7)];

        // Search Apr 13 or 14
        Calendar apr13 = Calendar.getInstance();
        apr13.set(year, Calendar.APRIL, 13);
        if (PY_TO_VAKYA[apr13.get(Calendar.DAY_OF_WEEK) - 1].equals(kyWkday)) {
            return apr13;
        }
        Calendar apr14 = Calendar.getInstance();
        apr14.set(year, Calendar.APRIL, 14);
        return apr14;
    }

    // Compute all 13 Tamil month start dates (index 0 = TNY, index 1..12 = months 2-13)
    Calendar[] findAllMonthStarts(int year) {
        if (monthStartsCache.containsKey(year)) return monthStartsCache.get(year);

        long[] cdef = kyYearArithmetic(year);
        int svA = (int)(cdef[0] % 7);
        int svB = (int) cdef[1];
        int svC = (int) cdef[2];
        int svD = (int) cdef[3];

        Calendar tny = findTamilNewYear(year);
        Calendar[] starts = new Calendar[13];
        starts[0] = tny;
        Calendar prev = tny;

        for (int i = 1; i <= 12; i++) {
            int[] p = SOLAR_MONTH_PARAMS[i];
            int dVal = p[3] + svD;
            int cVal = p[2] + svC;
            int bVal = p[1] + svB;
            int aVal = p[0] + svA;
            if (dVal >= 60) { dVal -= 60; cVal++; }
            if (cVal >= 60) { cVal -= 60; bVal++; }
            if (bVal >= 60) { bVal -= 60; aVal++; }

            int[] thresh = SOLAR_THRESH[i];
            int j14 = aVal + (bVal * 60 + cVal > thresh[0] * 60 + thresh[1] ? 1 : 0);
            String targetWd = WEEKDAYS[j14 % 7];

            Calendar found = null;
            for (int off = 29; off <= 32; off++) {
                Calendar cand = (Calendar) prev.clone();
                cand.add(Calendar.DAY_OF_YEAR, off);
                if (PY_TO_VAKYA[cand.get(Calendar.DAY_OF_WEEK) - 1].equals(targetWd)) {
                    found = cand;
                    break;
                }
            }
            if (found == null) {
                found = (Calendar) prev.clone();
                found.add(Calendar.DAY_OF_YEAR, 30);
            }
            starts[i] = found;
            prev = found;
        }
        monthStartsCache.put(year, starts);
        return starts;
    }

    // Convert a Calendar date to Tamil (gregorianYearOfTNY, month 1-12, day 1-based)
    int[] dateToTamilMonthDay(Calendar date) {
        Calendar tny = findTamilNewYear(date.get(Calendar.YEAR));
        int gy = date.get(Calendar.YEAR);
        if (calToJulianDay(date) < calToJulianDay(tny)) gy--;

        Calendar[] starts = findAllMonthStarts(gy);
        int dateJD = calToJulianDay(date);
        for (int m = 0; m < 12; m++) {
            int startJD = calToJulianDay(starts[m]);
            int nextJD  = calToJulianDay(starts[m + 1]);
            if (dateJD >= startJD && dateJD < nextJD) {
                return new int[]{gy, m + 1, dateJD - startJD + 1};
            }
        }
        int last = calToJulianDay(starts[11]);
        return new int[]{gy, 12, dateJD - last + 1};
    }

    private int calToJulianDay(Calendar cal) {
        int y = cal.get(Calendar.YEAR);
        int m = cal.get(Calendar.MONTH) + 1;
        int d = cal.get(Calendar.DAY_OF_MONTH);
        return julianDayNumber(y, m, d);
    }

    private int julianDayNumber(int y, int m, int d) {
        // Standard Gregorian JDN formula — requires TRUNCATED (not floor) division for 'a'
        int a = (m - 14) / 12;  // Java '/' truncates towards zero, which is correct here
        return Math.floorDiv(1461 * (y + 4800 + a), 4)
             + Math.floorDiv(367 * (m - 2 - 12 * a), 12)
             - Math.floorDiv(3 * Math.floorDiv(y + 4900 + a, 100), 4)
             + d - 32075;
    }

    private int calDiffDays(Calendar a, Calendar b) {
        return calToJulianDay(a) - calToJulianDay(b);
    }

    // ── Sunrise computation — exact port of ICS class i ────────────────────
    // Returns vinadi elapsed since sunrise, and the local date of sunrise.
    // vinadi = elapsed Tamil time units (1 vinadi = 24s, 3600 vinadi = 1 full day).
    // Faithful to InputActivity.b() vinadi formula and class i sunrise algorithm.

    // c(d) = d - (int)(d/360) * 360  [Java int truncates toward zero]
    private static double icsC(double d) {
        return d - ((int)(d / 360.0)) * 360.0;
    }

    private static double icsSinDeg(double d) {
        return Math.sin(d * 0.0174532925199433);
    }

    private static double icsCosDeg(double d) {
        return Math.cos(d * 0.0174532925199433);
    }

    // Exact port of class i a(Date date, double latArcsec, double lonArcsec, double tzArcsec, int mode)
    // lat/lon passed as arcseconds (degrees * 3600); tzHours in decimal hours.
    // mode=1 sunrise, mode=2 sunset.
    // Returns local solar time in hours [0, 24).
    double icsSunriseLocalHours(int year, int month, int day,
                                 double latArcsec, double lonArcsec,
                                 double tzHours, int mode) {
        // Java Calendar: month is 0-indexed; class i does i5 = month0 + 1
        // Here month is already 1-indexed (January=1), so i5 = month.
        int i5 = month;
        int yr = year;
        if (i5 <= 2) { i5 += 12; yr--; }

        // d7: days from J2000.0, using local calendar date (treating local midnight as UTC)
        // Java integer divisions truncate toward zero
        double d7 = ((yr * 365) - 730548.5)
                    + ((yr / 400) - (yr / 100))   // Java int/int = truncation
                    + (yr / 4)
                    + (int)((i5 + 1) * 30.6001)
                    + day
                    + 0.0;

        double d8 = latArcsec / 3600.0;  // lat degrees
        double d9 = lonArcsec / 3600.0;  // lon degrees

        double sinVal = Math.sin(0.0);    // = 0; no atmospheric refraction
        double sinLat = icsSinDeg(d8);
        double cosLat = icsCosDeg(d8);

        double d4, d5;
        if (mode == 1) {
            d4 = sinLat;
            d5 = 1.0;
        } else {
            d4 = sinLat;
            d5 = -1.0;
        }

        double d6  = 180.0;   // prevUT (initial, triggers first iteration)
        double d10 = 0.0;     // curUT (UTnew)

        while (Math.abs(d6 - d10) > 0.1) {
            double d11 = d7 + (d10 / 360.0);
            double d13 = d11 / 36525.0;                              // T

            double L   = icsC((36000.77 * d13) + 280.46);           // mean lon
            double d14 = (35999.05 * d13) + 357.528;                // mean anomaly G
            double d15 = d14 * 2.0;
            double a3  = L + (icsSinDeg(d14) * 1.915) + (icsSinDeg(d15) * 0.02); // lambda

            // Equation of time component E
            double a4 = (((icsSinDeg(d14) * (-1.915))
                         - (icsSinDeg(d15) * 0.02))
                         + (icsSinDeg(a3 * 2.0) * 2.466))
                        - (icsSinDeg(4.0 * a3) * 0.053);

            double d16 = 23.4393 - (0.13 * d13);                    // obliquity
            double d17 = (d10 - 180.0) + a4;                        // GHA

            // Solar declination
            double a5    = icsSinDeg(d16) * icsSinDeg(a3);
            double delta = Math.atan(a5 / Math.sqrt((-a5) * a5 + 1.0)) * 57.2957795130823;

            // Hour angle cosine
            double a6 = (sinVal - (icsSinDeg(delta) * d4)) / (icsCosDeg(delta) * cosLat);

            // Act = hour angle in degrees
            double d20 = -a6;
            double act = (Math.atan(d20 / Math.sqrt((d20 * a6) + 1.0))
                          + (Math.atan(1.0) * 2.0)) * 57.2957795130823;
            if (a6 > 1.0)  act = 0.0;
            if (a6 < -1.0) act = 180.0;

            d6  = d10;                                               // prevUT
            d10 = icsC(d6 - ((d17 + d9) + (d5 * act)));            // UTnew
        }

        // Convert UT degrees to local hours
        double d21 = (d10 / 15.0) + tzHours;
        if (d21 < 0.0)   d21 += 24.0;
        if (d21 >= 24.0) d21 -= 24.0;
        return d21;
    }

    long[] computeVinadiAndVakyaDate(int year, int month, int day,
                                      int hour, int minute,
                                      double lat, double lon, double tzHours) {
        // Work entirely in LOCAL time, matching ICS behavior.
        double birthLocalHours = hour + minute / 60.0;

        // ICS passes lat/lon in arcseconds to class i
        double latArcsec = lat * 3600.0;
        double lonArcsec = lon * 3600.0;

        double sunriseLocal = icsSunriseLocalHours(year, month, day,
                                                    latArcsec, lonArcsec, tzHours, 1);

        long vinadi;
        int srYear = year, srMonth = month, srDay = day;

        if (birthLocalHours < sunriseLocal) {
            // Pre-sunrise: Tamil day = previous calendar day
            // ICS: timeInMillis2 = 60 - (sunrise_ms - birth_ms)/3600000 * 2.5
            double diffHours = sunriseLocal - birthLocalHours;
            double nazhigai  = 60.0 - diffHours * 2.5;
            vinadi = (long)(nazhigai) * 60;
            // Decrement date
            srDay--;
            if (srDay < 1) {
                srMonth--;
                if (srMonth < 1) { srMonth = 12; srYear--; }
                srDay = daysInMonth(srYear, srMonth);
            }
        } else {
            // Post-sunrise: Tamil day = birth's calendar date
            // ICS: timeInMillis2 = (birth_ms - sunrise_ms)/3600000 * 2.5
            double diffHours = birthLocalHours - sunriseLocal;
            double nazhigai  = diffHours * 2.5;
            vinadi = (long)(nazhigai) * 60;
        }

        if (vinadi < 0) vinadi = 0;
        if (vinadi > 3599) vinadi = 3599;

        return new long[]{vinadi, srYear, srMonth, srDay};
    }

    private int daysInMonth(int y, int m) {
        int[] dims = {31,28,31,30,31,30,31,31,30,31,30,31};
        if (m == 2 && ((y%4==0 && y%100!=0) || y%400==0)) return 29;
        return dims[m - 1];
    }

    // ── l.java interpolation ────────────────────────────────────────────────
    // Returns {longitude_arcsec_times_1000, retrograde_0_or_1}

    double[] ljInterpolate(long todayArcSec, long tomorrowArcSec, long vinadi) {
        long j  = todayArcSec;
        long j2 = tomorrowArcSec;

        boolean goingBack = j > j2;
        long abs3 = Math.abs(j - j2);

        if (abs3 > 180000) {
            goingBack = !goingBack;
            long abs, abs2;
            if (goingBack) {
                abs  = FULL_CIRCLE - Math.abs(j2);
                abs2 = Math.abs(j);
            } else {
                abs  = FULL_CIRCLE - Math.abs(j);
                abs2 = Math.abs(j2);
            }
            abs3 = abs + abs2;
        }

        double d = (abs3 / 3600.0) * vinadi;
        double d2 = goingBack ? (j - d) : (j + d);
        if (d2 < 0.0) d2 += FULL_CIRCLE;

        double lonDeg = d2 / 3600.0;
        if (lonDeg >= 360.0) lonDeg -= 360.0;

        return new double[]{lonDeg % 360.0, goingBack ? 1.0 : 0.0};
    }

    // ── Sun ─────────────────────────────────────────────────────────────────
    // k.java g(Date): compute Sun arcsec at Tamil day (year, month, dayInMonth)

    long sunArcSecAtDate(int year, int month, int dayInMonth) {
        long[] cdef = kyYearArithmetic(year);
        long D = cdef[1], E = cdef[2], F = cdef[3];

        // Kshepa
        long j4, j3, j2, j;
        if (D * 60 + E < 1856) {
            j  = 15 - F;
            j2 = 31 - E;
            j3 = 15 - D;
            j4 = 365;
        } else {
            j  = 0 - F;
            j2 = 0 - E;
            j3 = 60 - D;
            j4 = 0;
        }
        if (j  < 0) { j  += 60; j2--; }
        if (j2 < 0) { j2 += 60; j3--; }
        if (j3 < 0) { j3 += 60; j4--; }
        if (j4 < 0) { j4 += 360; }

        // Manda correction
        int i3 = (int)(j4 / 10);
        if (i3 > 37) i3 = 0;
        long j9 = SUN_MANDA[i3];
        if (i3 > 36) i3 = 0;
        int grad = SUN_MANDA_GRAD[i3];
        long frac = (((j4 % 10) * 60 + j3) * 60 + j2) * 60 + j;
        double absCorr = (Math.abs(grad) * 60.0 * frac) / 216.0 / 1000.0;
        long j10 = j9 * 60 * 60;
        long j11 = grad > 0 ? (long)(j10 + absCorr) : (long)(j10 - absCorr);

        long j12 = j11 % 60;
        long j13 = j11 / 60;
        long j14 = j13 % 60;
        long j15 = j  - j12;
        long j16 = j2 - j14;
        long j17 = j3 - (j13 / 60) % 60;
        long j18 = j4 - (j13 / 60) / 60;
        if (j15 < 0) { j15 += 60; j16--; }
        if (j16 < 0) { j16 += 60; j17--; }
        if (j17 < 0) { j17 += 60; j18--; }
        if (j18 < 0) { j18 += 360; }

        // Day of year
        long j5;
        if (month == 1) {
            j5 = dayInMonth;
        } else {
            Calendar[] starts = findAllMonthStarts(year);
            Calendar startM   = starts[month - 1];
            Calendar startTNY = starts[0];
            j5 = calDiffDays(startM, startTNY) + dayInMonth;
        }

        // Daily accumulation
        for (long i5 = 0; i5 < j5 - 1; i5++) {
            int seg = (int) Math.min((i5 + 2) / 10, 36);
            int daily = SUN_DAILY_ARCSEC[seg];
            j17 += daily / 60;
            j16 += daily % 60;
            if (j16 >= 60) { j17++; j16 -= 60; }
            if (j17 >= 60) { j18++; j17 -= 60; }
            if (j18 >= 360) j18 -= 360;
        }

        return ((j18 * 60 + j17) * 60 + j16) % FULL_CIRCLE;
    }

    // ── Approximate Moon sidereal longitude (no ephem) ─────────────────────
    // Simplified Meeus formula; accurate to ~2° — sufficient for disambiguating
    // between Vakya table rows ~14° apart.

    double approximateMoonSidereal(double jd) {
        double T  = (jd - 2451545.0) / 36525.0;
        double T2 = T * T;
        double L0     = 218.3164477 + 481267.88123421*T - 0.0015786*T2 + T2*T/538841.0;
        double M      = 357.5291092 + 35999.0502909*T;
        double Mprime = 134.9633964 + 477198.8675055*T + 0.0087414*T2;
        double F      = 93.2720950  + 483202.0175233*T - 0.0036539*T2;
        double D      = 297.8501921 + 445267.1114034*T - 0.0018819*T2;
        double lonCorr = 6.288750 * Math.sin(Math.toRadians(Mprime))
                       + 1.274018 * Math.sin(Math.toRadians(2*D - Mprime))
                       + 0.658309 * Math.sin(Math.toRadians(2*D))
                       + 0.213616 * Math.sin(Math.toRadians(2*Mprime))
                       - 0.185116 * Math.sin(Math.toRadians(M))
                       - 0.114332 * Math.sin(Math.toRadians(2*F))
                       + 0.058793 * Math.sin(Math.toRadians(2*D - 2*Mprime))
                       + 0.057066 * Math.sin(Math.toRadians(2*D - M - Mprime))
                       + 0.053322 * Math.sin(Math.toRadians(2*D + Mprime))
                       + 0.045758 * Math.sin(Math.toRadians(2*D - M));
        double lon = ((L0 + lonCorr) % 360.0 + 360.0) % 360.0;
        // Lahiri ayanamsa approximation
        double year = 2000.0 + T * 100.0;
        double ayanamsa = 23.85 + (year - 1900.0) * 50.29 / 3600.0;
        return ((lon - ayanamsa) % 360.0 + 360.0) % 360.0;
    }

    // ── Moon ────────────────────────────────────────────────────────────────
    // k.java f(Date): compute Moon arcsec — uses sre.txt + hsg.txt

    long moonArcSecFromJ7(long j7, int month, int dayInMonth) {
        long a3 = SAKA_MONTHS[month - 1][0] + dayInMonth - 1;

        long j13 = 0;
        long j15 = j7;
        for (int i = 0; i < 38; i++) {
            if (j15 >= MOON_KHANDAS[i]) {
                j15 -= MOON_KHANDAS[i];
                j13 += MOON_ANCHORS[i];
            }
        }

        long j16 = j15 + a3;
        if (j16 > 248) { j16 -= 248; j13 += 99846; }
        if (j16 > 248) { j16 -= 248; j13 += 99846; }
        if (j16 == 0) j16 = 1;

        double[] vakRow = getRow("sre.txt", (int) j16);
        if (vakRow == null) return 0;
        long mBArcMin = (long) vakRow[1];

        double[] hsgRow = getRow("hsg.txt", dayInMonth);
        long monthCorr = (hsgRow != null && hsgRow.length > month - 1) ? (long) hsgRow[month - 1] : 0;

        return (j13 + mBArcMin * 60 + monthCorr) % FULL_CIRCLE;
    }

    // ── Rahu ────────────────────────────────────────────────────────────────
    // k.java e(Date): compute Rahu arcsec

    long rahuArcSecAtDate(long C, long D, long E, long F, int month, int dayInMonth) {
        int[] sm = SAKA_MONTHS[month - 1];
        long j  = C + sm[0] + dayInMonth - 1;
        long j2 = D + sm[1];
        long j3 = E + sm[2];
        if (F + sm[3] > 29) j3++;
        if (j3 >= 60) { j3 -= 60; j2++; }
        if (j2 >= 60) { j2 -= 60; j++; }

        long j4 = j - RAHU_KY_OFFSET;
        long j5 = j4 % RAHU_PERIOD;

        long i3 = j5 / RAHU_SUBCYCLE;
        long j6 = (j5 % RAHU_SUBCYCLE) * 30;
        long j7 = j6 / RAHU_SUBCYCLE + i3 * 30;
        long j8 = (j6 % RAHU_SUBCYCLE) * 60;
        long j9 = j8 / RAHU_SUBCYCLE;
        long j10 = (j8 % RAHU_SUBCYCLE) * 60 / RAHU_SUBCYCLE;

        long j11 = j4 / RAHU_MACRO;
        long j12 = ((j4 % RAHU_MACRO) * 30) / RAHU_MACRO;
        while (j12 >= 60) { j11++; j12 -= 60; }
        long j26 = 0;
        while (j11 >= 60) { j26++; j11 -= 60; }

        long j14 = j10 - j12;
        if (j14 < 0) { j14 += 60; j9--; }
        long j15 = j9 - j11;
        if (j15 < 0) { j15 += 60; j7--; }
        long j16 = (j7 - j26) % 360;

        // Speed correction
        double vnCombined = j2 * 60.0 + j3;
        double speedCorr = 0.0;
        double running = vnCombined;
        for (int idx = 0; idx < RAHU_SPEED_INC.length; idx++) {
            while (running >= RAHU_SPEED_LIMIT[idx]) {
                running   -= RAHU_SPEED_LIMIT[idx];
                speedCorr += RAHU_SPEED_INC[idx];
            }
        }

        double raw = (j16 * 60 + j15) * 60.0 + j14;
        double d4  = FULL_CIRCLE - (raw - speedCorr) - RAHU_BIJA_ARCSEC;
        if (d4 < 0.0) d4 += FULL_CIRCLE;
        return (long)(d4 % FULL_CIRCLE);
    }

    // ── Outer/inner planets (Mars, Jupiter, Venus, Saturn, Mercury) ─────────
    // k.java methods a/b/c/d/h — table lookup + interpolation

    Long planetRawArcSec(PlanetDesc desc,
                          long ky_C, long ky_D, long ky_E, long ky_F,
                          int month, int dayInMonth) {
        int[] sm = SAKA_MONTHS[month - 1];
        long day = ky_C + sm[0] + dayInMonth - 1;
        long gha = ky_D + sm[1];
        long vin = ky_E + sm[2];
        if (ky_F + sm[3] > 29) vin++;
        if (vin >= 60) { vin -= 60; gha++; }
        if (gha >= 60) { gha -= 60; day++; }
        long initGha = gha, initVin = vin;

        // Khanda reduction
        long accBija = 0;
        for (int ki = 0; ki < desc.khandas.length; ki++) {
            long khanda = desc.khandas[ki];
            int  gh     = desc.gh[ki];
            int  bija   = desc.bija[ki];
            while (desc.strict ? (day - khanda > 0) : (day - khanda >= 0)) {
                gha -= gh;
                if (gha >= 0 || day > 0) {
                    if (gha < 0 && day > 0) { gha += 60; day--; }
                    day -= khanda;
                    accBija += bija;
                } else {
                    gha += gh;
                    break;
                }
            }
        }
        if (day < 0) day = 0;

        long G        = day % desc.period;
        long cycleNum = day / desc.period;
        long expectedCycle = (desc.cycleMod != null)
            ? (cycleNum % desc.cycleMod) + 1
            : cycleNum + 1;

        // Row search
        Integer seqFound = null;
        for (int rowIdx = 1; rowIdx <= desc.rows; rowIdx++) {
            long seq = cycleNum * desc.rows + rowIdx;
            if (desc.name.equals("Saturn") && seq > 580) seq -= 578;
            String fname = seq > desc.split ? desc.fileHigh : desc.fileLow;
            double[] row = getRow(fname, (int) seq);
            if (row == null) continue;
            boolean cond = (desc.name.equals("Saturn"))
                ? ((long)row[0] == expectedCycle && (long)row[1] >= G)
                : ((long)row[0] == expectedCycle && (long)row[1] >  G);
            if (cond) {
                seqFound = (int) seq;
                break;
            }
        }
        if (seqFound == null) {
            long seq = cycleNum * desc.rows + desc.rows;
            if (desc.name.equals("Saturn") && seq > 580) seq -= 578;
            seqFound = (int) seq;
        }

        long seqF = seqFound;
        long seqP = seqFound - 1;
        if (desc.name.equals("Saturn") && seqP > 580) seqP -= 578;
        if (desc.name.equals("Saturn") && seqF > 580) seqF -= 578;

        String fnF = seqF > desc.split ? desc.fileHigh : desc.fileLow;
        String fnP = seqP > desc.split ? desc.fileHigh : desc.fileLow;
        double[] row2 = getRow(fnF, (int) seqF);
        double[] row1 = getRow(fnP, (int) seqP);

        if (row2 == null || row1 == null) return null;

        long deg2 = (long) row2[2], am2 = (long) row2[3];
        long deg1 = (long) row1[2], am1 = (long) row1[3];
        // c1/c2: bija correction columns — preserve as double (can be -0.5 etc.)
        double c2 = (row2.length > desc.col) ? row2[desc.col] : 0.0;
        double c1 = (row1.length > desc.col) ? row1[desc.col] : 0.0;
        long day2 = (long) row2[1], day1 = (long) row1[1];

        // Unwrap 0/360° seam
        if (deg1 < deg2 && (deg2 - deg1) > 300) deg1 += 360;
        if (deg1 > deg2 && (deg1 - deg2) > 300) deg2 += 360;

        // Build bracket arcsec (c1/c2 are double to preserve fractions)
        long bArcsec = accBija * 60;
        double pos1 = c1 * accBija + bArcsec + (deg1 * 60 + am1) * 60;
        double pos2 = bArcsec + accBija * c2 + (deg2 * 60 + am2) * 60;
        if (pos1 < 0 || pos2 < 0) { pos1 += FULL_CIRCLE; pos2 += FULL_CIRCLE; }

        double diff;
        boolean wrapped;
        if (Math.abs(Math.abs(pos2) - Math.abs(pos1)) <= 1080000) {
            diff    = Math.abs(pos2 - pos1);
            wrapped = false;
        } else {
            diff    = (pos1 + FULL_CIRCLE) - pos2;
            wrapped = true;
        }
        diff = Math.abs(diff);

        // Sub-day fraction
        long daySpan = (day2 - day1 != 0) ? (day2 - day1) : 1;
        long doff    = G - day1;
        long vinOff  = vin - initVin;
        if (vinOff < 0) { vinOff += 60; gha--; }
        long ghaOff  = gha - initGha;
        if (ghaOff < 0) { ghaOff += 60; doff--; }
        if (initGha >= 30) doff++;

        long fracNum = ((doff * 60 + ghaOff) * 60) + vinOff;
        double interp = (diff / (daySpan * 60L * 60L)) * fracNum;

        if (wrapped) pos1 += FULL_CIRCLE;
        double result = (pos1 > pos2) ? (pos1 - interp) : (pos1 + interp);
        return (long)(result) % FULL_CIRCLE;
    }

    // ── Main computation ────────────────────────────────────────────────────

    double[] computePlanets(int year, int month, int day,
                             int hour, int minute,
                             double lat, double lon, double tzHours) {
        // 1. Compute vinadi and Tamil date of sunrise
        long[] vaResult = computeVinadiAndVakyaDate(year, month, day, hour, minute, lat, lon, tzHours);
        long vinadi = vaResult[0];
        int srYear  = (int) vaResult[1];
        int srMonth = (int) vaResult[2];
        int srDay   = (int) vaResult[3];

        Calendar vakyaDate = Calendar.getInstance();
        vakyaDate.set(srYear, srMonth - 1, srDay);

        // 2. Tamil date for today's sunrise
        int[] tToday   = dateToTamilMonthDay(vakyaDate);
        int   gy       = tToday[0];
        int   tMonth   = tToday[1];
        int   tDay     = tToday[2];
        long[] cdef    = kyYearArithmetic(gy);
        long C = cdef[0], D = cdef[1], E = cdef[2], F = cdef[3];

        // 3. Tamil date for tomorrow
        Calendar tomorrow = (Calendar) vakyaDate.clone();
        tomorrow.add(Calendar.DAY_OF_YEAR, 1);
        int[] tTom    = dateToTamilMonthDay(tomorrow);
        int   gyTom   = tTom[0];
        int   t2Month = tTom[1];
        int   t2Day   = tTom[2];
        long CT, DT, ET, FT;
        if (gyTom != gy) {
            long[] cdefT = kyYearArithmetic(gyTom);
            CT=cdefT[0]; DT=cdefT[1]; ET=cdefT[2]; FT=cdefT[3];
        } else {
            CT=C; DT=D; ET=E; FT=F;
        }

        double[] result = new double[9]; // Sun,Moon,Mars,Mercury,Jupiter,Venus,Saturn,Rahu,Ketu

        // ── Sun ──────────────────────────────────────────────────────────────
        long sunToday    = sunArcSecAtDate(gy,    tMonth,  tDay);
        long sunTomorrow = sunArcSecAtDate(gyTom, t2Month, t2Day);
        double[] sunR    = ljInterpolate(sunToday, sunTomorrow, vinadi);
        result[0] = sunR[0] % 360.0;

        // ── Moon ─────────────────────────────────────────────────────────────
        long j7std = C + (D * 60 + E >= 1845 ? 1 : 0);

        // Compute approximate Moon sidereal longitude (Meeus simplified formula)
        // to disambiguate between j7std (delta=0) and j7std+1 (delta=1).
        // Convert birth UTC to Julian Day Number for the formula.
        {
            // UTC time: birth local time minus tzHours offset
            double localH = hour + minute / 60.0;
            double utcH   = localH - tzHours;
            // Adjust date if UTC crosses day boundary
            int utcY = year, utcM = month, utcD = day;
            while (utcH < 0)  { utcH += 24; utcD--; if (utcD < 1) { utcM--; if (utcM<1){utcM=12;utcY--;} utcD=daysInMonth(utcY,utcM); } }
            while (utcH >= 24) { utcH -= 24; utcD++; if (utcD > daysInMonth(utcY,utcM)) { utcM++; utcD=1; if(utcM>12){utcM=1;utcY++;} } }
            // julianDayNumber() returns the Julian Day Number (JDN) which corresponds to noon UTC.
            // So JD at arbitrary utcH hours = JDN + (utcH - 12.0) / 24.0
            double jdUTC = julianDayNumber(utcY, utcM, utcD) + (utcH - 12.0) / 24.0;
            double approxMoon = approximateMoonSidereal(jdUTC);

            // Pick delta=0 or delta=1 based on which table interpolation is closest
            long j7best = j7std;
            double bestDiff = Double.MAX_VALUE;
            for (int delta = -1; delta <= 2; delta++) {
                long j7cand = j7std + delta;
                long todayCand = moonArcSecFromJ7(j7cand, tMonth, tDay);
                long tomCand   = moonArcSecFromJ7(j7cand, t2Month, t2Day);
                double[] interp = ljInterpolate(todayCand, tomCand, vinadi);
                // Use floorMod for true modulo (Python-compatible), not Java '%' remainder
                double raw = interp[0] - approxMoon + 180.0;
                double modded = raw - 360.0 * Math.floor(raw / 360.0);  // true modulo
                double diff = Math.abs(modded - 180.0);
                if (diff < bestDiff) { bestDiff = diff; j7best = j7cand; }
            }
            long moonToday    = moonArcSecFromJ7(j7best, tMonth,  tDay);
            long moonTomorrow = moonArcSecFromJ7(j7best, t2Month, t2Day);
            double[] moonR    = ljInterpolate(moonToday, moonTomorrow, vinadi);
            result[1] = moonR[0] % 360.0;
        }

        // ── Table planets ─────────────────────────────────────────────────────
        // Mars=2, Jupiter=4, Venus=5, Saturn=6, Mercury=3
        int[] resultIdxMap = {2, 4, 5, 6, 3};  // Mars,Jupiter,Venus,Saturn,Mercury
        for (int pi = 0; pi < PLANETS.length; pi++) {
            PlanetDesc pd = PLANETS[pi];
            Long pToday    = planetRawArcSec(pd, C,  D,  E,  F,  tMonth,  tDay);
            Long pTomorrow = planetRawArcSec(pd, CT, DT, ET, FT, t2Month, t2Day);
            if (pToday == null)    { result[resultIdxMap[pi]] = 0.0; continue; }
            if (pTomorrow == null) pTomorrow = pToday;
            double[] pr = ljInterpolate(pToday, pTomorrow, vinadi);
            result[resultIdxMap[pi]] = pr[0] % 360.0;
        }

        // ── Rahu / Ketu ───────────────────────────────────────────────────────
        long rahuToday    = rahuArcSecAtDate(C,  D,  E,  F,  tMonth,  tDay);
        long rahuTomorrow = rahuArcSecAtDate(CT, DT, ET, FT, t2Month, t2Day);
        double[] rahuR    = ljInterpolate(rahuToday, rahuTomorrow, vinadi);
        result[7] = rahuR[0] % 360.0;
        result[8] = (result[7] + 180.0) % 360.0;

        return result;
    }

    // ── main() ──────────────────────────────────────────────────────────────

    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.err.println("Usage: java VakkiamEngine <vakya_data_dir>");
            System.exit(1);
        }
        String dataDir = args[0];
        VakkiamEngine engine = new VakkiamEngine(dataDir);

        double LAT     = 11.6643;
        double LON     = 78.185;
        double TZ      = 5.5;

        BufferedReader stdin = new BufferedReader(new InputStreamReader(System.in));
        String line;
        while ((line = stdin.readLine()) != null) {
            line = line.trim();
            if (line.isEmpty()) continue;
            String[] parts = line.split("\\|");
            if (parts.length < 6) continue;
            String idx   = parts[0];
            int year     = Integer.parseInt(parts[1]);
            int month    = Integer.parseInt(parts[2]);
            int day      = Integer.parseInt(parts[3]);
            int hour     = Integer.parseInt(parts[4]);
            int minute   = Integer.parseInt(parts[5]);

            double lat = LAT, lon = LON, tz = TZ;
            if (parts.length >= 7) lat    = Double.parseDouble(parts[6]);
            if (parts.length >= 8) lon    = Double.parseDouble(parts[7]);
            if (parts.length >= 9) tz     = Double.parseDouble(parts[8]);

            try {
                double[] planets = engine.computePlanets(year, month, day, hour, minute, lat, lon, tz);
                // Output: idx|Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn|Rahu|Ketu
                StringBuilder sb = new StringBuilder();
                sb.append(idx);
                for (double p : planets) {
                    sb.append("|");
                    sb.append(String.format("%.6f", p));
                }
                System.out.println(sb.toString());
            } catch (Exception e) {
                System.err.println("Error on case " + idx + ": " + e.getMessage());
                System.out.println(idx + "|0|0|0|0|0|0|0|0|0");
            }
        }
    }
}
