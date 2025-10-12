import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface ChartProps {
  houses: { [key: number]: string[] };
  title: string;
}

const SouthIndianChart: React.FC<ChartProps> = ({ houses, title }) => {
  const renderCell = (sign: number) => {
    const labels = houses[sign] || [];
    
    // Find Ascendant/Lagna
    const ascIdx = labels.findIndex(x => 
      ["Asc", "Lagna", "லக்"].includes(x)
    );
    
    let ascLabel = null;
    let planetLabels = [...labels];
    
    if (ascIdx >= 0) {
      ascLabel = labels[ascIdx];
      planetLabels.splice(ascIdx, 1);
    }

    return (
      <View key={sign} style={styles.cell}>
        <Text style={styles.signNumber}>{sign}</Text>
        <Text style={styles.planetStack}>
          {planetLabels.join('\n')}
        </Text>
        {ascLabel && (
          <Text style={styles.lagna}>{ascLabel}</Text>
        )}
      </View>
    );
  };

  return (
    <View style={styles.chart}>
      {/* Row 1 */}
      {renderCell(1)}
      {renderCell(2)}
      {renderCell(3)}
      {renderCell(4)}
      
      {/* Row 2 */}
      {renderCell(12)}
      <View style={[styles.cell, styles.center]}>
        <Text style={styles.centerText}>{title}</Text>
      </View>
      <View style={[styles.cell, styles.centerHidden]} />
      {renderCell(5)}
      
      {/* Row 3 */}
      {renderCell(11)}
      <View style={[styles.cell, styles.centerHidden]} />
      <View style={[styles.cell, styles.centerHidden]} />
      {renderCell(6)}
      
      {/* Row 4 */}
      {renderCell(10)}
      {renderCell(9)}
      {renderCell(8)}
      {renderCell(7)}
    </View>
  );
};

const styles = StyleSheet.create({
  chart: {
    width: 360,
    height: 360,
    backgroundColor: '#FFFBEA',
    borderWidth: 2,
    borderColor: '#333',
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 2,
    gap: 2,
  },
  cell: {
    width: 'calc(25% - 2px)',
    height: 'calc(25% - 2px)',
    borderWidth: 1,
    borderColor: '#333',
    padding: 6,
    position: 'relative',
  },
  center: {
    width: 'calc(50% - 2px)',
    height: 'calc(50% - 2px)',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 0,
  },
  centerHidden: {
    borderWidth: 0,
    backgroundColor: 'transparent',
  },
  centerText: {
    fontWeight: '700',
    fontSize: 16,
    textAlign: 'center',
  },
  signNumber: {
    position: 'absolute',
    right: 6,
    top: 4,
    opacity: 0.55,
    fontSize: 10,
  },
  lagna: {
    position: 'absolute',
    right: 6,
    bottom: 6,
    transform: [{ rotate: '-30deg' }],
    fontSize: 10,
    fontStyle: 'italic',
  },
  planetStack: {
    fontSize: 12,
    lineHeight: 16,
  },
});

export default SouthIndianChart;
