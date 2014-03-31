import pandas

def _sw(df, up_rows=10, down_rows=5, left_cols=4, right_cols=3, return_df=False, labels_limit=100):
    ''' display df data at four corners
        A,B (up_pt)
        C,D (down_pt)
        parameters : up_rows=10, down_rows=5, left_cols=4, right_cols=3
        usage:
            df = pd.DataFrame(np.random.randn(20,10), columns=list('ABCDEFGHIJKLMN')[0:10])
            df.sw(5,2,3,2)
            df1 = df.set_index(['A','B'], drop=True, inplace=False)
            df1.sw(5,2,3,2)
    '''
    #pd.set_printoptions(max_columns = 80, max_rows = 40)
    ncol, nrow = len(df.columns), len(df)

    # handle columns
    if ncol <= (left_cols + right_cols) :
        up_pt = df.ix[0:up_rows, :]         # screen width can contain all columns
        down_pt = df.ix[-down_rows:, :]
    else:                                   # screen width can not contain all columns
        pt_a = df.ix[0:up_rows,  0:left_cols]
        pt_b = df.ix[0:up_rows,  -right_cols:]
        pt_c = df[-down_rows:].ix[:,0:left_cols]
        pt_d = df[-down_rows:].ix[:,-right_cols:]

        up_pt   = pt_a.join(pt_b, how='inner')
        down_pt = pt_c.join(pt_d, how='inner')
        up_pt.insert(left_cols, '..', '..')
        down_pt.insert(left_cols, '..', '..')

        max_width = max(map(len, up_pt.index) + map(len, down_pt.index))
        up_pt.index = [str(x).ljust(max_width) for x in up_pt.index]
        down_pt.index = [str(x).ljust(max_width) for x in down_pt.index]

    overlap_qty = len(up_pt) + len(down_pt) - len(df)
    down_pt = down_pt.drop(down_pt.index[range(overlap_qty)]) # remove overlap rows

    dt_str_list = down_pt.to_string().split('\n') # transfer down_pt to string list

    # Display up part data
    print up_pt.to_string()

    start_row = (1 if df.index.names[0] is None else 2) # start from 1 if without index

    # Display omit line if screen height is not enought to display all rows
    if overlap_qty < 0:
        print "." * len(dt_str_list[start_row])

    # Display down part data row by row
    for line in dt_str_list[start_row:]:
        print line

    # Display foot note
    print "\n"
    if len(df.index) > labels_limit:
        print "Index :", ", ".join(map(str, df.index[:int(labels_limit/2.0)].tolist()))
        print "..."
        print ", ".join(map(str, df.index[-int(labels_limit/2.0):].tolist()))
    else:
        print "Index :", ", ".join(map(str, df.index.tolist()))

    if len(df.columns) > labels_limit:
        print "Column:", ", ".join(map(str, list(df.columns[:int(labels_limit/2.0)].tolist())))
        print "..." 
        print ", ".join(map(str, list(df.columns[-int(labels_limit/2.0):].tolist())))
    else:
        print "Column:", ", ".join(map(str, list(df.columns.values)))

    print "rows: %d    cols: %d"%(len(df), len(df.columns))
    print "\n"

    return (df if return_df else None)
pandas.DataFrame.sw = _sw  #add a method to DataFrame class