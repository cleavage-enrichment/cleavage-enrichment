import { JSX } from "react";
import { styled } from "styled-components";
import { ProteinViewProps } from "./ProteinView.props";


const Table = styled.table`
 border-collapse: collapse;
`;

const Cell = styled.td`
  padding: 0;
  height: 10px;
`;

const PeptideBar = styled.div`
  height: 1px;
  width: 100%;
  background-color: green;
  border-radius-top-left: 5px;
  height: 5px;
`;

export const ProteinView: React.FC<ProteinViewProps> = ({protein, peptides}) => {
  const proteinLength = protein.length;  
  
  return (
    <div className="overflow-auto">
      <Table className="table-fixed border-collapse">
        <tbody>
          {/* Protein sequence row */}
          <tr>
            {protein.split("").map((aa, index) => (
              <Cell key={index} className={aa == 'R' ? "border-l-2 border-dotted border-black" : ""}>
                {aa}
              </Cell>
            ))}
          </tr>

          {/* Peptide rows */}
          {peptides.map((peptide, rowIndex) => {
            const cells: JSX.Element[] = [];

            // Empty cells before the peptide starts
            for (let i = 0; i < peptide.start - 1; i++) {
              cells.push(
                <Cell key={`empty-${i}`}/>
              );
            }

            // Cells for the peptide sequence
            for (let j = 0; j < peptide.sequence.length; j++) {
              cells.push(
                <Cell key={`peptide-${j}`}>
                  {peptide.sequence[j]}
                </Cell>
              );
            }

            // Fill remaining cells to maintain full row length
            const remaining = proteinLength - (peptide.start - 1 + peptide.sequence.length);
            for (let k = 0; k < remaining; k++) {
              cells.push(
                <Cell key={`filler-${k}`}/>
              );
            }

            return <tr key={rowIndex}>{cells}</tr>;
          })}

          {/* Peptide bar rows */}
          {peptides.map((peptide, rowIndex) => {
            const cells: JSX.Element[] = [];

            for (let i = 1; i <= proteinLength; i++) {
              const inPeptide = i >= peptide.start && i <= peptide.start + peptide.sequence.length - 1;
              cells.push(
                <Cell key={i}>
                  {inPeptide ? (
                    <PeptideBar className={i == peptide.start? "rounded-l" : i == peptide.start + peptide.sequence.length - 1 ? "rounded-r":""}/>
                  ) : null}
                </Cell>
              );
            }

            return <tr key={rowIndex}>{cells}</tr>;
          })}
        </tbody>
      </Table>
    </div>
  );
}